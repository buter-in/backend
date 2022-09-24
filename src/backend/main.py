from typing import Dict, Any, List
import asyncio
import json

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from web3 import Web3
import httpx

from eth_account.datastructures import SignedMessage
from eth_account.messages import encode_structured_data


API = "https://ipfs-api.quantor.me/api/v0"
IMG_BRO_HASH = "Qmbgmgg5xyfX7TCUgMhecBv8MhZeS9hnxTwD86AnCayq8z"
IMG_NEWB_HASH = "QmdpLaMgL7yFjt2rUtQ1cDVyzmsVLRFwoYMBpXJxtHRYWp"


def gen_eip712_message(from_addr: str, to_addr: str, nonce: int, path: str):
    return {
        "types": {
            "EIP712Domain": [
                {"name": "name", "type": "string"},
                {"name": "version", "type": "string"},
                {"name": "chainId", "type": "uint256"},
                {"name": "verifyingContract", "type": "address"},
            ],
            "approveSBT": [
                {"name": "emitent", "type": "address"},
                {"name": "to", "type": "address"},
                {"name": "nonce", "type": "uint256"},
                {"name": "path", "type": "string"},
            ],
        },
        "primaryType": "approveSBT",
        "domain": {
            "name": "SBT",
            "version": "1",
            "chainId": 31337,
            "verifyingContract": "0x6B21b3ae41f818Fc91e322b53f8D0773d31eCB75",
        },
        "message": {"emitent": from_addr, "to": to_addr, "nonce": nonce, "path": path},
    }


def sign_message(message: Dict[str, Any]) -> SignedMessage:
    w3 = Web3()
    priv_key = "59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d"
    w3.eth.default_account = w3.eth.account.privateKeyToAccount(priv_key)

    signed = w3.eth.default_account.sign_message(encode_structured_data(message))
    return signed


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


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/ping")
async def root():
    return "pong"


@app.post("/sbt_emitent_signature")
async def sbt_emitent_signature(
    from_addr: str = Query(..., regex="^0x[0-9a-fA-F]{40}$"),
    to_addr: str = Query(..., regex="^0x[0-9a-fA-F]{40}$"),
):
    paths = await get_shortest_path(from_addr=from_addr, to_addr=to_addr)
    ipfs_hash = IMG_BRO_HASH if paths else IMG_NEWB_HASH

    message = gen_eip712_message(
        from_addr=from_addr,
        to_addr=to_addr,
        nonce=0,
        path=f"ipfs://{ipfs_hash}",
    )
    signed = sign_message(message=message)
    signed_dict = {
        "messageHash": signed.messageHash.hex(),
        "r": signed.r,
        "s": signed.s,
        "v": signed.v,
        "signature": signed.signature.hex(),
    }

    json_data = {
        "image": f"ipfs://{ipfs_hash}",
        "name": "Buterin SBT collection",
        "description": "SBT collection of paths to Vitalik Buterin",
        "rank": "BRO" if paths else "NEWB",
        "paths": paths,
    }
    json_data_dump = json.dumps(json_data, ensure_ascii=False).encode()
    ipfs_hash = (await upload_to_ipfs(data=json_data_dump))["Hash"]
    return {
        **json_data,
        "message": message,
        "signed": signed_dict,
        "image_gw": f"{API}/cat?arg={ipfs_hash}",
        "json_ipfs": f"ipfs://{ipfs_hash}",
        "json_gw": f"{API}/cat?arg={ipfs_hash}",
    }


if __name__ == "__main__":
    # from_addr = "0xe3411d7Ba6e99D4228E304ED1bbb4dFF14813070"
    from_addr = "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"
    to_addr = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"

    # x = asyncio.run(get_shortest_path(from_addr, to_addr))
    x = asyncio.run(sbt_emitent_signature(from_addr, to_addr))
    # x = asyncio.run(upload_to_ipfs(data=b"ayylmao"))
    print(x)
    exit(1)
