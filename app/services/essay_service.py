"""
Essay service for IELTS essay reading
"""
import json
from typing import List, Dict, Any
from app.data.writing_corpus import get_ielts_essays


def get_all_essays(brief: bool = False, preview_len: int = 200) -> List[Dict[str, Any]]:
    """Get all IELTS essays. Use brief mode to avoid heavy payloads."""
    essays = get_ielts_essays()
    if not brief:
        return essays

    summaries: List[Dict[str, Any]] = []
    for essay in essays:
        body_text = essay.get("body_text", "")
        preview = body_text[:preview_len]
        if len(body_text) > preview_len:
            preview += "..."
        summaries.append(
            {
                "essay_number": essay.get("essay_number"),
                "title": essay.get("title"),
                "question": essay.get("question"),
                "word_count_reported": essay.get("word_count_reported"),
                "word_count_actual": essay.get("word_count_actual"),
                "preview": preview,
            }
        )
    return summaries


def get_essay_by_id(essay_id: int) -> Dict[str, Any] | None:
    """Get a specific essay by ID."""
    essays = get_ielts_essays()
    for essay in essays:
        if essay.get("essay_number") == essay_id:
            return essay
    return None


