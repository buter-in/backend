from typing import List

import httpx


async def get_shortest_path(from_addr: str, to_addr: str) -> List[str]:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.quantor.me/v1/eth/graph/fraud/shortest_path",
            headers={
                "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiODc3ZDJhYzgtOThlNi00NmNlLThhZTEtODU1NThiMDc3YTc0IiwiYXVkIjpbImZhc3RhcGktdXNlcnM6YXV0aCIsImZhc3RhcGktdXNlcnM6dmVyaWZ5Il19.pxjkPMfuPhtb11MSApFb_Zob3beSGHp-qJBrLS9HXE4"
            },
            json={
                "src": int(from_addr, 0),
                "dst": int(to_addr, 0),
            },
        )

        arrows = response.json()
        if not isinstance(arrows, list):
            return []

        head = arrows[0]["node_from"]
        tail = [arrow["node_to"] for arrow in arrows]
        return [head] + tail
