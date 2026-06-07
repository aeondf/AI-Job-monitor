import os
import time

import requests
import streamlit as st

API_URL = os.getenv("AI_JOB_MONITOR_API_URL", "http://localhost:8000")


def start_search(text: str, profile: str, limit: int) -> str:
    response = requests.post(
        f"{API_URL}/search",
        json={"text": text, "profile": profile, "limit": limit},
        timeout=15,
    )
    response.raise_for_status()
    return response.json()["search_id"]


def load_history() -> list[dict]:
    response = requests.get(f"{API_URL}/history", timeout=15)
    response.raise_for_status()
    return response.json()


def find_search(search_id: str) -> dict | None:
    for item in load_history():
        if item["search_id"] == search_id:
            return item
    return None


st.set_page_config(page_title="AI Job Monitor", layout="wide")

st.title("AI Job Monitor")
st.caption("Real job search + local RAG ranking")

with st.sidebar:
    st.header("Search")
    query = st.text_input("Vacancy query", value="python backend")
    limit = st.slider("Results", min_value=3, max_value=20, value=10)
    profile = st.text_area(
        "Candidate profile",
        value=(
            "Python backend developer. FastAPI, async/await, REST API, "
            "WebSocket, PostgreSQL, Docker, Redis, LLM/RAG systems."
        ),
        height=180,
    )

    start = st.button("Start search", type="primary", use_container_width=True)

if "search_id" not in st.session_state:
    st.session_state.search_id = None

if start:
    st.session_state.search_id = start_search(query, profile, limit)

if not st.session_state.search_id:
    st.info("Start a search from the sidebar.")
    st.stop()

placeholder = st.empty()

search = None
for _ in range(30):
    search = find_search(st.session_state.search_id)
    if search and search.get("status") != "running":
        break
    with placeholder.container():
        st.status("Searching real job sources and ranking vacancies...", expanded=True)
        if search:
            st.write(search.get("message", "Running"))
    time.sleep(1)

if not search:
    st.error("Search not found.")
    st.stop()

placeholder.empty()

status = search.get("status")
st.subheader(f"Search: {search.get('text')}")
st.write(search.get("message", ""))

if status == "failed":
    st.error(search.get("message", "Search failed."))
    st.stop()

jobs = search.get("jobs", [])

if not jobs:
    st.warning("No vacancies found yet. Refresh or try a broader query.")
    st.stop()

for job in jobs:
    with st.container(border=True):
        left, right = st.columns([4, 1])

        with left:
            st.markdown(f"### [{job.get('title')}]({job.get('url')})")
            st.write(
                " · ".join(
                    part
                    for part in [
                        job.get("company"),
                        job.get("location"),
                        job.get("source"),
                    ]
                    if part
                )
            )
            st.write(job.get("explanation"))

            matched = job.get("matched_terms") or []
            if matched:
                st.caption("Matched terms: " + ", ".join(matched[:12]))

            description = job.get("description") or ""
            with st.expander("Description"):
                st.write(description[:3000])

        with right:
            st.metric("Fit", f"{job.get('score', 0)}%")
            if job.get("salary"):
                st.caption(job["salary"])
