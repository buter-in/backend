from typing import Any, Dict, Union

from eth_account.datastructures import SignedMessage
from eth_account.messages import encode_structured_data
from web3 import Web3


def gen_eip712_message(to_addr: str, nonce: int, path: str):
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
            "name": "SBToken Buterin",
            "version": "1",
            "chainId": 80001,
            "verifyingContract": "0x9fc7cbe0aebb56d1a9f01a79ecfa3c32032021ae",
        },
        "message": {
            "emitent": "0xda32c0d780e780e6fcd1ef5d0d9e98a311f736f1",
            "to": to_addr,
            "nonce": nonce,
            "path": path,
        },
    }


def sign_message(message: Dict[str, Any]) -> SignedMessage:
    w3 = Web3()
    private_key = "54fe55fa9c4ac5a845f2d9033ae9ff50d9f855edcdcb670821b0a447f7c19a43"
    account = w3.eth.account.privateKeyToAccount(private_key)

    signed = account.sign_message(encode_structured_data(message))
    return signed


def signed_message_to_dict(signed: SignedMessage) -> Dict[str, Union[str, int]]:
    return {
        "messageHash": signed.messageHash.hex(),
        "r": signed.r,
        "s": signed.s,
        "v": signed.v,
        "signature": signed.signature.hex(),
    }
