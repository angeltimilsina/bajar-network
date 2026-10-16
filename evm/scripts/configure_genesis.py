#!/usr/bin/env python3
"""Adapt Besu's generated *local* QBFT genesis into a BAJ-denominated devnet.

Never use the included public development accounts for mainnet.
Run before starting any nodes. Changing genesis on a live chain is not supported.
"""
import argparse
import json
from pathlib import Path

CHAIN_ID = 131313
SUPPLY_BAJ = 13_000_000_000
WEI_PER_BAJ = 10**18
# PUBLICLY KNOWN BESU QUICKSTART TEST ACCOUNTS -- NOT PRODUCTION WALLETS.
DEV_FAUCET = "0x627306090abab3a6e1400e9345bc60c78a8bef57"
DEV_RESERVE = "0xf17f52151ebef6c7334fad080c5704d77216b732"
FAUCET_BAJ = 3_000_000_000
RESERVE_BAJ = 10_000_000_000

def configure(genesis):
    if not isinstance(genesis.get("config", {}).get("qbft"), dict):
        raise ValueError("Expected generated QBFT genesis; refusing to patch")
    if not genesis.get("extraData"):
        raise ValueError("Missing QBFT validator extraData")
    if genesis["config"].get("chainId") not in (1337, CHAIN_ID):
        raise ValueError("Unexpected chain ID; refusing to modify custom genesis")
    genesis["config"]["chainId"] = CHAIN_ID
    genesis["config"]["zeroBaseFee"] = True
    # Zero protocol minting. Standard transaction fees can redistribute/burn value.
    genesis["config"]["qbft"].pop("blockreward", None)

    # Preserve Besu's system/permissioning contracts, but remove all preset
    # ordinary balances and any inline sample private keys.
    system = {}
    for addr, account in genesis.get("alloc", {}).items():
        if "code" in account or "storage" in account:
            item = {k: v for k, v in account.items() if k not in ("privateKey", "comment")}
            item["balance"] = "0"
            system[addr.lower()] = item
    if DEV_FAUCET in system or DEV_RESERVE in system:
        raise ValueError("Development treasury collides with a system contract")

    system[DEV_FAUCET] = {"balance": str(FAUCET_BAJ * WEI_PER_BAJ)}
    system[DEV_RESERVE] = {"balance": str(RESERVE_BAJ * WEI_PER_BAJ)}
    genesis["alloc"] = system
    assert sum(int(v.get("balance", "0"), 0) if str(v.get("balance", "0")).startswith("0x")
               else int(v.get("balance", "0")) for v in system.values()) == SUPPLY_BAJ * WEI_PER_BAJ
    return genesis

def main():
    p = argparse.ArgumentParser()
    p.add_argument("genesis", type=Path)
    args = p.parse_args()
    original = json.loads(args.genesis.read_text(encoding="utf-8"))
    configured = configure(original)
    args.genesis.write_text(json.dumps(configured, indent=2) + "\n", encoding="utf-8")
    print("BAJAR genesis configured: chain ID %s, 4 generated QBFT validators" % CHAIN_ID)
    print("Genesis: 13,000,000,000 BAJ (3B dev faucet / 10B dev reserve)")
    print("CAUTION: publicly known test-wallet keys; local development ONLY.")

if __name__ == "__main__":
    main()

