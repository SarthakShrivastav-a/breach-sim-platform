from __future__ import annotations

import os
from typing import Any

import httpx


class WorkerClient:
    def __init__(self, api_base_url: str | None = None) -> None:
        self.api_base_url = (api_base_url or os.getenv("API_BASE_URL") or "http://localhost:8000").rstrip("/")

    async def run_scenario(self, scenario_id: str, requested_by: str = "worker") -> dict[str, Any]:
        async with httpx.AsyncClient(base_url=self.api_base_url, timeout=30) as client:
            response = await client.post(
                "/api/exercises",
                json={
                    "scenario_id": scenario_id,
                    "requested_by": requested_by,
                    "role": "Exercise Director",
                },
            )
            response.raise_for_status()
            return response.json()

