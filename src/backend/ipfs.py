from typing import Dict

import httpx


async def upload_to_ipfs(data: bytes) -> Dict[str, str]:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://ipfs-api.quantor.me/api/v0/add",
            params={
                "pin": "true",
                "wrap-with-directory": "false",
            },
            files=[("file", data)],
        )

        return response.json()


def ipfs_gateway_path(cid: str) -> str:
    return f"https://ipfs.io/ipfs/{cid}"


def get_vitalik_image_hash(is_bro: bool) -> str:
    bro = "Qmbgmgg5xyfX7TCUgMhecBv8MhZeS9hnxTwD86AnCayq8z"
    newb = "QmdpLaMgL7yFjt2rUtQ1cDVyzmsVLRFwoYMBpXJxtHRYWp"
    return [newb, bro][is_bro]
