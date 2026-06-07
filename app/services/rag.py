import re
from typing import Any

STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "the",
    "to",
    "with",
    "в",
    "и",
    "на",
    "не",
    "по",
    "с",
    "для",
    "от",
    "это",
    "как",
}


def tokenize(text: str) -> set[str]:
    words = re.findall(r"[a-zA-Zа-яА-Я0-9+#.]+", text.lower())
    return {word for word in words if len(word) > 1 and word not in STOP_WORDS}


def build_vacancy_text(vacancy: dict[str, Any]) -> str:
    tags = " ".join(vacancy.get("tags") or [])
    return " ".join(
        [
            vacancy.get("title") or "",
            vacancy.get("company") or "",
            vacancy.get("location") or "",
            vacancy.get("salary") or "",
            tags,
            vacancy.get("description") or "",
        ]
    )


def make_explanation(
    vacancy: dict[str, Any],
    matched_terms: list[str],
    query_tokens: set[str],
) -> str:
    title = vacancy.get("title") or "Vacancy"
    company = vacancy.get("company") or "unknown company"

    if matched_terms:
        terms = ", ".join(matched_terms[:8])
        return (
            f"{title} at {company} looks relevant because the vacancy text matches "
            f"these profile/search terms: {terms}."
        )

    if query_tokens:
        return (
            f"{title} at {company} was returned by the job source, but the local "
            "retriever found only weak overlap with your profile."
        )

    return f"{title} at {company} is included as a fresh job result."


def rank_vacancies(
    vacancies: list[dict[str, Any]],
    query: str,
    profile: str = "",
    limit: int = 10,
) -> list[dict[str, Any]]:
    query_tokens = tokenize(f"{query} {profile}")

    ranked: list[dict[str, Any]] = []

    for vacancy in vacancies:
        doc_text = build_vacancy_text(vacancy)
        doc_tokens = tokenize(doc_text)
        title_tokens = tokenize(vacancy.get("title") or "")
        tags_tokens = tokenize(" ".join(vacancy.get("tags") or []))

        matched = sorted(query_tokens & doc_tokens)
        weighted_matches = 0.0

        for token in matched:
            if token in title_tokens:
                weighted_matches += 3
            elif token in tags_tokens:
                weighted_matches += 2
            else:
                weighted_matches += 1

        denominator = max(len(query_tokens), 1)
        score = round(min((weighted_matches / denominator) * 100, 100), 1)

        enriched = {
            **vacancy,
            "score": score,
            "matched_terms": matched,
            "explanation": make_explanation(vacancy, matched, query_tokens),
        }
        ranked.append(enriched)

    ranked.sort(key=lambda item: item["score"], reverse=True)
    return ranked[:limit]
