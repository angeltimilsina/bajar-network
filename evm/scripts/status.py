#!/usr/bin/env python3
"""Smoke-check local BAJAR RPC without external dependencies."""
import json
import sys
from urllib.request import Request, urlopen
from urllib.error import URLError

RPC = "http://127.0.0.1:8545"
FAUCET = "0x627306090abab3a6e1400e9345bc60c78a8bef57"
RESERVE = "0xf17f52151ebef6c7334fad080c5704d77216b732"

def rpc(method, params=None):
    body = json.dumps({"jsonrpc":"2.0", "id":1, "method":method,
                       "params":params or []}).encode()
    req = Request(RPC, data=body, headers={"Content-Type":"application/json"})
    with urlopen(req, timeout=8) as response:
        data = json.load(response)
    if data.get("error"):
        raise RuntimeError(str(data["error"]))
    return data["result"]

def main():
    try:
        chain_id = int(rpc("eth_chainId"), 16)
        height = int(rpc("eth_blockNumber"), 16)
        balances = [int(rpc("eth_getBalance", [a, "latest"]), 16) for a in (FAUCET, RESERVE)]
    except (URLError, TimeoutError, RuntimeError) as e:
        print("Cannot reach BAJAR RPC at %s: %s" % (RPC, e), file=sys.stderr)
        return 1
    print("RPC: %s | Chain ID: %d | Latest block: %d" % (RPC, chain_id, height))
    for name, wei in zip(("Dev faucet", "Dev reserve"), balances):
        print("%s: %d BAJ (whole coin units)" % (name, wei // 10**18))
    if chain_id != 131313:
        print("ERROR: wrong chain ID", file=sys.stderr)
        return 1
    try:
        validators = rpc("qbft_getValidatorsByBlockNumber", ["latest"])
        print("QBFT validators: %d" % len(validators))
        if len(validators) != 4:
            print("ERROR: expected 4 validators", file=sys.stderr)
            return 1
    except (RuntimeError, URLError) as exc:
        print("Validator RPC check unavailable: %s" % exc, file=sys.stderr)
        return 1
    print("BAJAR EVM development network RPC verified.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

