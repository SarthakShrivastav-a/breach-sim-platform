from __future__ import annotations

import argparse
import asyncio
import json

from app.client import WorkerClient


async def _run(args: argparse.Namespace) -> None:
    client = WorkerClient(args.api_base_url)
    result = await client.run_scenario(args.scenario_id, args.requested_by)
    print(json.dumps(result, indent=2, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser(description="Breach simulation worker")
    parser.add_argument("--api-base-url", default=None)
    parser.add_argument("--scenario-id", default="SCN-001")
    parser.add_argument("--requested-by", default="worker")
    args = parser.parse_args()
    asyncio.run(_run(args))


if __name__ == "__main__":
    main()

