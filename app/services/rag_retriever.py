# app/services/rag_retriever.py
from app.data.writing_corpus import get_writing_corpus


def retrieve_similar_continuations(context: str, top_k: int = 3) -> list:
    """
    Simple keyword-based RAG for demo.
    In real version, replace with vector similarity (e.g., sentence-BERT + Chroma).
    """
    corpus = get_writing_corpus()
    context_lower = context.lower()

    # Simple keyword matching (you can enhance this later)
    keywords = {
        'technology': ['technology', 'internet', 'digital', 'online', 'ai', 'app'],
        'environment': ['environment', 'pollution', 'climate', 'carbon', 'eco', 'green'],
        'education': ['education', 'school', 'student', 'learn', 'teach', 'academic'],
        'society': ['society', 'government', 'policy', 'law', 'people', 'social'],
        'general': ['important', 'issue', 'problem', 'solution', 'study', 'research']
    }

    matched = []
    for category, words in keywords.items():
        if any(w in context_lower for w in words):
            # Add category-specific phrases
            for phrase in corpus:
                if category in phrase or any(kw in phrase for kw in words):
                    matched.append(phrase)
                    if len(matched) >= top_k:
                        return matched[:top_k]

    # Fallback: return general academic phrases
    general_phrases = [p for p in corpus if 'empirical' in p or 'debate' in p or 'warrants' in p]
    return (matched + general_phrases)[:top_k]