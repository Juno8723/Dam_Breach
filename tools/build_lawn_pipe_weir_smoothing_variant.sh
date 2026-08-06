#!/usr/bin/env bash
# Diagnostic-only experiment for docs/LAWN_PIPE_WEIR_TRANSITION_DIAGNOSTIC.md.
#
# The original 1999 NWS BREACH source contains a pipe-flow-to-weir-flow
# transition smoothing calculation (QEXP/QTR, src/breach1999_documented_corrections.f
# around L988-995) whose actual application to QB is commented out with a
# "CCC" prefix -- present in original/SRC/Breach.for:849-851 unchanged, i.e.
# this is a pre-existing (not this-project-introduced) piece of dead code.
#
# This script generates a THROWAWAY variant that uncomments exactly those 3
# lines (nothing else) and builds it as a separate binary, so its output can
# be compared against the real bin/breach1999_corrected without touching
# src/breach1999_documented_corrections.f, original/, or any input file.
#
# This variant is NOT used by any regression test and is NOT wired into the
# normal build (tests/build_corrected.sh). It exists solely to answer the
# question "does uncommenting this change the LAWN.DAT pipe-to-weir
# discontinuity, and if so, how" -- see docs/LAWN_PIPE_WEIR_TRANSITION_DIAGNOSTIC.md
# for the result and why this was NOT adopted into the real corrected source.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTDIR="$ROOT/tests/attribution/variants"
mkdir -p "$OUTDIR" "$ROOT/bin"

VARIANT="$OUTDIR/lawn_pipe_weir_smoothing_enabled.f"

python3 - "$ROOT/src/breach1999_documented_corrections.f" "$VARIANT" <<'PYEOF'
import sys
src, dst = sys.argv[1], sys.argv[2]
with open(src, "rb") as f:
    lines = f.read().split(b"\n")
targets = {
    992: b"CCC      IF(HCPCHK.GT.3.) QB=QTR",
    993: b"CCC      IF(HCPCHK.LE.3..AND.QTR.LE.QPMAX) QB=QTR",
    994: b"CCC      IF(HCPCHK.LE.3..AND.QTR.GT.QPMAX) QB=QPMAX",
}
for idx0, expected in targets.items():
    assert lines[idx0] == expected, f"line {idx0+1} mismatch: {lines[idx0]!r} -- source may have changed since this script was written"
    lines[idx0] = b"   " + lines[idx0][3:]
with open(dst, "wb") as f:
    f.write(b"\n".join(lines))
print(f"wrote {dst}")
PYEOF

gfortran \
  -std=legacy \
  -ffixed-form \
  -cpp \
  -O0 \
  -fno-range-check \
  "$VARIANT" \
  -o "$ROOT/bin/breach1999_lawn_pipe_weir_smoothing_enabled"

echo "Built bin/breach1999_lawn_pipe_weir_smoothing_enabled from $VARIANT"
