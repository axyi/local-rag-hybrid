import re

import requests

from config import KEYWORD_TIMEOUT, MAX_KEYWORDS, OLLAMA_MODEL, OLLAMA_URL

KEYWORD_PROMPT = (
    "Extract 3 to 6 search keywords or short key phrases from the user question. "
    "Answer with ONLY the keywords, comma-separated, in the same language as the question.\n"
    "\n"
    "Question: {question}\n"
    "Keywords:"
)


def expand_query(question: str) -> list[str]:
    """Extract search keywords from a question via the local LLM; never raises."""
    try:
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": KEYWORD_PROMPT.format(question=question),
            "stream": False,
            "think": False,
            "options": {"temperature": 0.0, "num_predict": 100},
        }
        response = requests.post(OLLAMA_URL, json=payload, timeout=KEYWORD_TIMEOUT)
        if response.status_code != 200:
            return []
        raw = response.json()["response"]
        text = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL)
        parts = re.split(r"[,\n]", text)

        question_lower = question.strip().lower()
        seen: set[str] = set()
        keywords: list[str] = []
        for part in parts:
            cleaned = part.strip()
            cleaned = cleaned.strip("-•*\"'`")
            cleaned = cleaned.strip()
            if cleaned.endswith("."):
                cleaned = cleaned[:-1]

            if not cleaned or len(cleaned) > 80:
                continue
            lowered = cleaned.lower()
            if lowered in seen or lowered == question_lower:
                continue

            seen.add(lowered)
            keywords.append(cleaned)
            if len(keywords) == MAX_KEYWORDS:
                break

        return keywords
    except Exception:
        return []
