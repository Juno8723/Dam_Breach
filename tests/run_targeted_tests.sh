#!/usr/bin/env bash
# Runs every hand-built synthetic edge-case input in tests/targeted/*.dat
# through both the reference (unmodified 1999) and corrected binaries,
# saving results under outputs/targeted/<case>/ and printing a summary.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

for dat in "$ROOT"/tests/targeted/*.dat; do
  name="$(basename "$dat" .dat)"
  outdir="$ROOT/outputs/targeted/$name"
  mkdir -p "$outdir"
  for label in reference corrected; do
    bin="$ROOT/bin/breach1999_$label"
    work="$(mktemp -d)"
    cp "$dat" "$work/in.dat"
    (cd "$work" && "$bin" > stdout.txt 2> stderr.txt)
    code=$?
    cp "$work/stdout.txt" "$outdir/$label.stdout.txt"
    cp "$work/stderr.txt" "$outdir/$label.stderr.txt"
    echo "$code" > "$outdir/$label.exitcode.txt"
    if [ "$code" -eq 0 ]; then
      python3 "$ROOT/tools/parse_breach_output.py" "$outdir/$label.stdout.txt" \
        -o "$outdir/$label.parsed.json" --no-hydrograph
    fi
    rm -rf "$work"
    echo "[$name] $label: exit=$code"
  done
done

echo
echo "=== summary ==="
for dat in "$ROOT"/tests/targeted/*.dat; do
  name="$(basename "$dat" .dat)"
  outdir="$ROOT/outputs/targeted/$name"
  ref_code="$(cat "$outdir/reference.exitcode.txt" 2>/dev/null || echo '?')"
  cor_code="$(cat "$outdir/corrected.exitcode.txt" 2>/dev/null || echo '?')"
  echo "$name: reference exit=$ref_code, corrected exit=$cor_code"
done
