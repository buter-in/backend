from typing import Any, Dict

from web3 import Web3

from eth_account.datastructures import SignedMessage
from eth_account.messages import encode_structured_data


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
            "name": "SBToken Buterin",
            "version": "1",
            "chainId": 80001,
            "verifyingContract": "0x9fc7cbe0aebb56d1a9f01a79ecfa3c32032021ae",
        },
        "message": {"emitent": from_addr, "to": to_addr, "nonce": nonce, "path": path},
    }


def sign_message(message: Dict[str, Any]) -> SignedMessage:
    w3 = Web3()
    priv_key = "59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d"
    w3.eth.default_account = w3.eth.account.privateKeyToAccount(priv_key)

    signed = w3.eth.default_account.sign_message(encode_structured_data(message))
    return signed
