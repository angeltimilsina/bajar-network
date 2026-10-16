# BAJAR Network — EVM QBFT Local Devnet

An independent, **local-only EVM blockchain** powered by Hyperledger Besu and QBFT.
This is separate from the repository's existing experimental Rust ledger.
No Wormhole, external deployment gas, or existing L1 is needed for this local development network.

> **Not a mainnet.** Do not use this setup for real assets or public trading.

## Prerequisites

- Docker Desktop / Docker Engine with Compose v2 (allocate **6 GB RAM**).
- Node.js and npx, Python 3, Bash.
- On Windows, use WSL2 with Docker Desktop WSL integration, then run these commands inside WSL.
- MetaMask or a compatible injected EVM wallet, for optional browser testing.

## Start locally

From the cloned repository root:

\`\`\`bash
bash evm/scripts/start.sh
\`\`\`

The script uses the [official Besu Developer Quickstart](https://docs.besu-eth.org/private-networks/tutorials/quickstart/)
to generate **four QBFT validators and one separate RPC node**. Before the first block,
it modifies the generated QBFT genesis to use BAJ's chain ID and supply.
Generated validator keys, database files, and Compose files stay ignored at
\`evm/.generated/besu-test-network/\` and are **not committed to GitHub**.

After Docker finishes initializing:

\`\`\`bash
python3 evm/scripts/status.py
\`\`\`

The script checks the chain ID, block height, two development account balances,
and four-validator QBFT set. If the network is still booting, retry the command.

### Local network configuration

| Item | Value |
|---|---|
| Network name | BAJAR Devnet (Local) |
| RPC | http://127.0.0.1:8545 |
| Chain ID | 131313 (0x200f1) |
| Native coin | BAJ |
| EVM native decimals | 18 |
| Wallet display precision | 9 fractional digits |
| Consensus | QBFT, four local validators |
| Gas | Zero base fee on this development network |

Supply is allocated at genesis, **not minted by an ERC-20 contract**:

- Public dev faucet wallet: \`0x627306090abaB3A6e1400e9345bC60c78a8BEf57\` — 3,000,000,000 BAJ.
- Public dev reserve wallet: \`0xf17f52151EbEF6C7334FAD080c5704D77216b732\` — 10,000,000,000 BAJ.
- Genesis total: **13,000,000,000 BAJ**. No QBFT block reward is configured.

**Both wallet private keys are publicly documented sample keys.**
The reserve allocation is only a *simulation*; it is not locked or vested.
Never send valuable assets to these addresses on any network.

For development-only transactions, import the example account key from
[Besu's official quickstart documentation](https://docs.besu-eth.org/private-networks/tutorials/quickstart/#6-send-a-transaction-with-metamask).
Never use it for any production network.

### Connect wallet

From the repository root, start a separate terminal:

\`\`\`bash
python3 -m http.server 5173 --directory evm/wallet
\`\`\`

Browse to **http://127.0.0.1:5173** and click **Connect MetaMask & add BAJAR Devnet**.
Approve the network and account requests. You can read native BAJ balances and submit
wallet-approved **test** transfers. For manually adding the chain in MetaMask,
use the configuration table above. Wallet balance is displayed to nine fractional digits;
the EVM's underlying native arithmetic still uses 18 decimals.

### Stop or reset

\`\`\`bash
cd evm/.generated/besu-test-network
bash ./stop.sh
\`\`\`

Never change the genesis of a running chain. To **destroy all local chain state**
and start a *fresh and unrelated* devnet, stop the containers, remove the generated
Compose containers/volumes, then delete \`evm/.generated/besu-test-network/\`
and rerun the startup script. Back up anything you care about first.

### Tests

\`\`\`bash
python3 -m unittest discover -s evm/tests -v
bash -n evm/scripts/start.sh
\`\`\`

The repository CI validates the genesis patcher but **does not** run Docker
consensus or transaction end-to-end tests.

## Public mainnet pathway — not deployed

1. Decide on a *separate* public chain ID; publish immutable genesis and chain spec.
2. Replace every developer key with offline-generated, independently controlled validator keys; retain at least four operationally independent validators.
3. Set final 13B issuance, audited treasury custody, allocation policies, real reserve vesting/lockups, and rules disallowing unapproved inflation. Native EVM uses 18 decimals; restricting protocol-level precision to nine decimals needs additional engineering.
4. Choose validator admission/governance rules. QBFT begins as a permissioned-validator model; it does **not** automatically give permissionless proof-of-stake decentralization.
5. Deploy across multiple machines and providers; configure bootnodes, P2P endpoints, TLS/restricted RPC gateways, monitoring, backups, block explorers, chain registry entries, and disaster recovery.
6. Commission independent consensus, infrastructure, smart-contract, custody, and economic security reviews. Address exchange/payment regulatory requirements before selling or listing BAJ.
7. Operate a public testnet and adversarial tests first. Only then consider production launch, validators, bridges, exchanges, and liquidity.

**Limitations:** Local validators share one machine and one operator. The devnet's
supply follows genesis balances and absence of block rewards, but there is no
separate immutable "max supply" opcode in the EVM. Future consensus upgrades,
governance, or bridges could change global supply; mainnet needs explicit controls.
The existing Rust prototype still uses an older, independent 108M-coin configuration
and is not consensus-compatible with this EVM devnet.

