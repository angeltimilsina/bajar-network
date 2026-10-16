# Bajar Network

Experimental independent Layer 1 blockchain development project.

## Two independent prototypes

**EVM / QBFT devnet — new:** [Run BAJAR EVM devnet](evm/README.md). A local
Hyperledger Besu network with four QBFT validators, a JSON-RPC node, a native BAJ
genesis allocation of **13,000,000,000 BAJ**, and a small browser wallet demo.
The configuration is development-only and has not been launched publicly.

**Rust ledger — existing:** The \`bajar-core\` crate remains an experimental in-memory
Ed25519 ledger. It has no production consensus, RPC, network or EVM execution.
Its earlier hardcoded 108,000,000 coin supply is separate from the new EVM devnet
and should not be interpreted as current BAJAR tokenomics.

## Run Rust tests

\`\`\`bash
cargo test --workspace
\`\`\`

## Next milestones

- Confirm native BAJ supply, allocation and precision policy for a sovereign L1.
- Test EVM transfers, contract deployments, validator participation and failure handling.
- Add independent validator operators and public testnet infrastructure.
- Complete security, custody, economic and compliance reviews before considering mainnet.

**Warning:** No publicly launched BAJAR blockchain or tradable native coin is
established by this repository. Do not use the prototypes for real funds.

