# Bajar Network

Experimental independent Layer 1 blockchain development project.

## Architecture goal
Bajar Framework: Rust ledger, signatures, P2P networking, BFT consensus, deterministic execution, and future smart-contract runtime.

BAJAR is intended to be the network's native asset, with a fixed genesis supply of **13,000,000,000 BAJAR (9 decimals)**. The experimental ledger encodes these supply units but does not yet enforce circulating supply, lockups, token vesting, or governance.

## Proposed launch allocation (not yet implemented)

- **3,000,000,000 BAJAR** allocated for potential launch circulation.
- **10,000,000,000 BAJAR** designated as non-circulating reserves, subject to independently verified custody, lockups, and an approved release schedule.
- **Important:** The current `Ledger::genesis` assigns the entire supply to a single treasury account. These allocation figures are a proposed policy only; they do **not** currently establish circulating supply or enforce reserve locks. Vesting and actual distribution must be implemented and tested before launch.

## Current implementation
The `bajar-core` crate contains an **experimental in-memory ledger** with Ed25519 signed transfers, nonces, chain-ID replay protection, genesis supply, and deterministic state hashing. It has no network, consensus, persistent database, fee market, or production security review.

## Run tests
```bash
cargo test --workspace
```

## Next milestones
1. Persist ledger state and implement canonical transaction encoding.
2. Integrate a studied BFT consensus engine; implement validator membership and block production.
3. Add P2P transport, sync, RPC, and four-node devnet.
4. Implement staking economics, transaction fees, and adversarial testing.
5. Add audited Wasm smart contracts and stablecoin integrations.

**Warning:** No real BAJAR coins exist on a public network yet. Do not use with real funds.
