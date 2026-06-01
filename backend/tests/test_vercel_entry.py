from fastapi import FastAPI

from server import app


def test_vercel_entry_exports_fastapi_app() -> None:
    assert isinstance(app, FastAPI)
