from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import grafana, health, search, stations


def create_app() -> FastAPI:
    app = FastAPI(title="chargeflow-influxDB", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health.router)
    app.include_router(stations.router)
    app.include_router(grafana.router)
    app.include_router(search.router)
    return app


app = create_app()
