import asyncio
import re
from html import unescape
from typing import Any

import httpx


def clean_text(value: str | None, max_length: int = 2500) -> str:
    if not value:
        return ""

    text = re.sub(r"<[^>]+>", " ", value)
    text = unescape(text)
    text = re.sub(r"\s+", " ", text).strip()

    return text[:max_length]


def normalize_remotejobs_item(item: dict[str, Any]) -> dict[str, Any]:
    company = item.get("company") or {}
    category = item.get("category") or {}

    return {
        "id": str(item.get("id") or ""),
        "title": item.get("title") or "",
        "url": item.get("apply_url") or item.get("url") or "",
        "company": company.get("name") if isinstance(company, dict) else str(company),
        "location": item.get("location") or "",
        "salary": item.get("salary_text") or "",
        "tags": [category.get("name")] if isinstance(category, dict) else [],
        "description": clean_text(item.get("description")),
        "source": "remotejobs",
    }


def normalize_remotive_item(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(item.get("id") or ""),
        "title": item.get("title") or "",
        "url": item.get("url") or "",
        "company": item.get("company_name") or "",
        "location": item.get("candidate_required_location") or "",
        "salary": item.get("salary") or "",
        "tags": item.get("tags") or [],
        "description": clean_text(item.get("description")),
        "source": "remotive",
    }


def normalize_remoteok_item(item: dict[str, Any]) -> dict[str, Any]:
    salary_min = item.get("salary_min") or 0
    salary_max = item.get("salary_max") or 0
    salary = ""

    if salary_min or salary_max:
        salary = f"${salary_min:,} - ${salary_max:,}"

    return {
        "id": str(item.get("id") or ""),
        "title": item.get("position") or "",
        "url": item.get("apply_url") or item.get("url") or "",
        "company": item.get("company") or "",
        "location": item.get("location") or "Remote",
        "salary": salary,
        "tags": item.get("tags") or [],
        "description": clean_text(item.get("description")),
        "source": "remoteok",
    }


async def fetch_remotejobs_vacancies(
    text: str, limit: int = 20
) -> list[dict[str, Any]]:
    url = "https://remotejobs.org/api/v1/jobs"
    params = {
        "keyword": text,
        "limit": min(max(limit, 1), 50),
    }

    async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

    return [normalize_remotejobs_item(item) for item in data.get("data", [])]


async def fetch_remotive_vacancies(text: str, limit: int = 20) -> list[dict[str, Any]]:
    url = "https://remotive.com/api/remote-jobs"
    params = {"search": text}

    async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

    jobs = [normalize_remotive_item(item) for item in data.get("jobs", [])]
    return jobs[:limit]


async def fetch_remoteok_vacancies(limit: int = 50) -> list[dict[str, Any]]:
    url = "https://remoteok.com/api"
    headers = {"User-Agent": "AIJobMonitor/0.1"}

    async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

    jobs = [
        normalize_remoteok_item(item)
        for item in data[1:]
        if isinstance(item, dict) and item.get("id")
    ]
    return jobs[:limit]


async def fetch_real_vacancies(text: str, limit: int = 20) -> list[dict[str, Any]]:
    per_source_limit = max(limit, 10)
    results = await asyncio.gather(
        fetch_remotejobs_vacancies(text, per_source_limit),
        fetch_remotive_vacancies(text, per_source_limit),
        fetch_remoteok_vacancies(limit=50),
        return_exceptions=True,
    )

    vacancies: list[dict[str, Any]] = []

    for result in results:
        if isinstance(result, Exception):
            print("Job source failed:", repr(result))
            continue
        vacancies.extend(result)

    seen: set[str] = set()
    unique_vacancies: list[dict[str, Any]] = []

    for vacancy in vacancies:
        key = vacancy.get("url") or f"{vacancy.get('source')}:{vacancy.get('id')}"
        if key in seen:
            continue
        seen.add(key)
        unique_vacancies.append(vacancy)

    return unique_vacancies
