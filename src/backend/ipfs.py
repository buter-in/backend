from typing import Dict

import httpx


API = "https://ipfs-api.quantor.me/api/v0"
IMG_BRO_HASH = "Qmbgmgg5xyfX7TCUgMhecBv8MhZeS9hnxTwD86AnCayq8z"
IMG_NEWB_HASH = "QmdpLaMgL7yFjt2rUtQ1cDVyzmsVLRFwoYMBpXJxtHRYWp"


async def upload_to_ipfs(data: bytes) -> Dict[str, str]:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API}/add",
            params={
                "pin": "true",
                "wrap-with-directory": "false",
            },
            files=[("file", data)],
        )

        return response.json()
