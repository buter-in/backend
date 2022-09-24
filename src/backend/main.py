import asyncio
import json

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware


from backend.crypto import gen_eip712_message, sign_message
from backend.ipfs import upload_to_ipfs
from backend.pathfind import get_shortest_path

API = "https://ipfs-api.quantor.me/api/v0"
IMG_BRO_HASH = "Qmbgmgg5xyfX7TCUgMhecBv8MhZeS9hnxTwD86AnCayq8z"
IMG_NEWB_HASH = "QmdpLaMgL7yFjt2rUtQ1cDVyzmsVLRFwoYMBpXJxtHRYWp"


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
        to_addr=from_addr,
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
