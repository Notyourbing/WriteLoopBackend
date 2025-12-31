# app/services/suggest_service.py
import json
import re
from app.services.llm_client import client, OPENAI_MODEL
from app.services.rag_retriever import retrieve_similar_continuations


def generate_suggestions(text: str, cursor: dict, read_essay_ids: list = None) -> str:
    """
    Generate 3 high-quality, academically appropriate ENGLISH PHRASES 
    that can naturally follow the user's current text.

    - Input: full text (we use last ~100 chars as context)
    - Output: 3 phrases (2-8 words), with explanations, in JSON
    """
    if not text.strip():
        return json.dumps({"suggestions": []})

    # Use last 100 characters as context to avoid token overflow
    context = text[-100:].strip()

    # Retrieve relevant examples based on reading history for RAG enhancement
    retrieved_examples = retrieve_similar_continuations(context, top_k=3, read_essay_ids=read_essay_ids)

    # Build strong-constraint prompt
    prompt = f"""
    You are an IELTS writing coach. The student is composing an academic English essay.

    Current text they have written:
    "{context}"

    They are about to continue writing. Your task is to suggest EXACTLY 3 natural, advanced, and exam-appropriate ENGLISH PHRASES 
    that can LOGICALLY and GRAMMATICALLY FOLLOW this text — as if the student is continuing their sentence.

    CRITICAL RULES:
    1. Each phrase must be 2 to 8 words long.
    2. Use formal, academic vocabulary (Band 7+ or CET-6 level).
    3. NEVER use: "and", "but", "so", "I think", "very", "good", "bad", "help", "make", "thing", "stuff".
    4. MUST be grammatically compatible with the current sentence structure.
       - If the current sentence ends with a noun (like "air pollution"), the suggestion should start with a verb or relative clause.
       - Example: "which significantly harms public health" OR "that exacerbates climate change"
    5. Avoid standalone sentences — only provide continuations that complete the existing thought.
    6. If possible, echo the style of these real examples:
    {chr(10).join([f' - "{ex}"' for ex in retrieved_examples])}

    Return a STRICT JSON object with this structure:
    {{
      "suggestions": [
        {{
          "text": "exact phrase here",
          "explain": "1-sentence teaching note: why this phrase is strong AND grammatically correct in context"
        }},
        ...
      ]
    }}
    DO NOT add any other text, markdown, or explanation outside the JSON.
    """
    try:
        completion = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},  # Enforce JSON
            max_completion_tokens=2000
        )
        result = completion.choices[0].message.content or ""
        result = result.strip()
        if not result:
            raise ValueError("Empty LLM response")

        try:
            parsed = json.loads(result)
        except json.JSONDecodeError:
            # Some models may wrap JSON in extra text; try to extract the JSON object.
            match = re.search(r"\{.*\}", result, re.DOTALL)
            if not match:
                raise
            parsed = json.loads(match.group(0))

        return json.dumps(parsed, ensure_ascii=False)
    except Exception as e:
        print(f"Suggestion generation error: {e}")
        # Fallback: return safe empty response
        return json.dumps({"suggestions": []})
