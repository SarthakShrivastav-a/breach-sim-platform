from __future__ import annotations

from worker.app.client import WorkerClient


def test_worker_client_uses_explicit_base_url():
    client = WorkerClient("http://api.internal:8000/")
    assert client.api_base_url == "http://api.internal:8000"

