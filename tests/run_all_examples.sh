#!/usr/bin/env bash
# Runs every example input through a given BREACH binary and stores raw
# stdout/stderr plus a parsed JSON summary under outputs/<label>/.
#
# Usage: run_all_examples.sh <binary> <label>
#   e.g. run_all_examples.sh bin/breach1999_reference baseline
#        run_all_examples.sh bin/breach1999_corrected corrected
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BIN="${1:?usage: run_all_examples.sh <binary> <label>}"
LABEL="${2:?usage: run_all_examples.sh <binary> <label>}"
OUTDIR="$ROOT/outputs/$LABEL"
mkdir -p "$OUTDIR"

for dat in "$ROOT"/examples/*.DAT; do
  name="$(basename "$dat" .DAT)"
  work="$(mktemp -d)"
  cp "$dat" "$work/in.dat"
  set +e
  (cd "$work" && "$ROOT/$BIN" > stdout.txt 2> stderr.txt)
  exit_code=$?
  set -e
  cp "$work/stdout.txt" "$OUTDIR/$name.stdout.txt"
  cp "$work/stderr.txt" "$OUTDIR/$name.stderr.txt"
  echo "$exit_code" > "$OUTDIR/$name.exitcode.txt"
  python3 "$ROOT/tools/parse_breach_output.py" "$OUTDIR/$name.stdout.txt" \
    -o "$OUTDIR/$name.parsed.json"
  rm -rf "$work"
  echo "[$LABEL] $name: exit=$exit_code"
done
