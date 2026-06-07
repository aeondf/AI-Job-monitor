AI Job Monitor
==============

Small FastAPI + Streamlit project for searching real remote job sources and
ranking vacancies against a candidate profile.

Run backend:

```bash
uv run uvicorn main:app --port 8001
```

Run UI in a second terminal:

```bash
AI_JOB_MONITOR_API_URL=http://localhost:8001 uv run streamlit run streamlit_app.py
```

Main API endpoints:

- `GET /sources`
- `POST /search`
- `GET /history`
- `GET /debug/rag`

Current job sources:

- RemoteJobs.org
- Remotive
- RemoteOK

The RAG layer is local for now: it retrieves vacancies from real APIs, builds a
document text for each vacancy, ranks them by overlap with the search query and
candidate profile, then generates a short explanation from matched terms.
