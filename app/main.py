from fastapi import FastAPI

from app.routers import debug, history, search, sources


def create_app() -> FastAPI:
    app = FastAPI(title="AI Job Monitor")

    app.include_router(sources.router)
    app.include_router(search.router)
    app.include_router(history.router)
    app.include_router(debug.router)

    return app


app = create_app()
