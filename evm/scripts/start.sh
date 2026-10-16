#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/evm/.generated/besu-test-network"
GENESIS="$OUT/config/besu/genesis.json"

for tool in docker node npx python3; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    echo "Missing $tool. See evm/README.md" >&2; exit 1
  fi
done
docker compose version >/dev/null

if [ ! -f "$GENESIS" ]; then
  if [ -e "$OUT" ]; then
    echo "Found incomplete network folder: $OUT; inspect it before retrying." >&2; exit 1
  fi
  mkdir -p "$(dirname "$OUT")"
  echo "Generating official Besu QBFT quickstart files..."
  npx --yes @consensys-software/besu-dev-quickstart \
    --networkType private --outputPath "$OUT" --otel false --chainlens false
  test -f "$GENESIS" || { echo "Generator did not create expected genesis path" >&2; exit 1; }
  python3 "$ROOT/evm/scripts/configure_genesis.py" "$GENESIS"
else
  python3 - "$GENESIS" <<'PY'
import json,sys
data=json.load(open(sys.argv[1],encoding="utf-8"))
if data.get("config",{}).get("chainId") != 131313:
    sys.exit("Existing genesis is not BAJAR devnet; refusing to change an initialized chain")
PY
fi

echo "Starting local validators and RPC node..."
cd "$OUT"
bash ./run.sh
echo "After nodes initialize: python3 evm/scripts/status.py (from repository root)"

