#!/usr/bin/bash
set -euo pipefail

# where your JSON lives
INPUT_DIR="./time_period_runs"
# where you want the outputs
OUTPUT_DIR="./portfolio_output"
# same for every run
START_CAPITAL=1000000

mkdir -p "$OUTPUT_DIR"

for json_file in "$INPUT_DIR"/*.json; do
  # e.g. cluster_returns_hierarchical_3m_n1.json → cluster_returns_hierarchical_3m_n1
  base=$(basename "$json_file" .json)
  # strip the leading "cluster_returns_" → hierarchical_3m_n1
  suffix=${base#cluster_returns_}
  out_csv="$OUTPUT_DIR/${suffix}.csv"

  echo "=============================="
  echo "Backtesting: $base"
  echo "→ output → $out_csv"
  echo

  python Backtester.py \
    "$json_file" \
    "$START_CAPITAL" \
    "$out_csv"
done

echo
echo "All backtests complete."
