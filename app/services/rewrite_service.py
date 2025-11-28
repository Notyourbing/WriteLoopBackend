from app.services.llm_client import client
import json

def rewrite_sentence(sentence: str) -> str:
    """
    根据用户输入的句子，通过 OpenAI API 进行句子改写
    """
    # 设计一个严格的 prompt，要求返回的句子是英文的改写版
    prompt = f"Rewrite this sentence in better English: {sentence}"

    # 构建消息列表，传递给 OpenAI
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ]

    try:
        # 调用 OpenAI API 获取改写后的句子
        completion = client.chat.completions.create(model="gpt-4o-mini", messages=messages)

        # 获取模型返回的文本（应为改写后的句子）
        rewritten_text = completion.choices[0].message.content.strip()

        # 构建返回的字典
        response = {
            "original": sentence,
            "rewritten": rewritten_text
        }

        # 返回 JSON 格式的响应
        return json.dumps(response)

    except Exception as e:
        print(f"Error generating rewritten sentence: {e}")
        # 返回空 JSON 数组，表示错误
        return json.dumps({"error": str(e)})

