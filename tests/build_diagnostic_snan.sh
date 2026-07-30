#!/usr/bin/env bash
# Diagnostic builds (both reference and corrected sources) that poison
# uninitialized memory to make read-before-write bugs fail loudly and
# deterministically, instead of silently reading whatever the loader/OS
# happened to leave behind (the suspected cause of negative-BMX
# non-determinism -- see docs/NEGATIVE_BMX_DIAGNOSTIC.md).
#
#   -finit-real=snan       every REAL starts as a signaling NaN
#   -finit-integer=-999999 every INTEGER starts at a very unlikely sentinel
#   -ffpe-trap=invalid,... traps the moment a signaling NaN is used in an
#                           arithmetic op, instead of quietly propagating
#
# These do NOT change any computed value for a correctly-initialized
# program; they only change what happens to READS of memory the program
# never wrote. This is intentionally a *diagnostic-only* build, separate
# from tests/build_reference.sh / tests/build_corrected.sh.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
mkdir -p "$ROOT/bin"

FLAGS=(
  -std=legacy -ffixed-form -O0 -g
  -Wall -Wextra -Wconversion
  -fcheck=all -fbacktrace
  -finit-real=snan -finit-integer=-999999
  -ffpe-trap=invalid,zero,overflow
)

gfortran "${FLAGS[@]}" "$ROOT/src/breach1999_reference.f" \
  -o "$ROOT/bin/breach1999_reference_snan" \
  2> "$ROOT/bin/breach1999_reference_snan.diagnostics.txt" || true

gfortran "${FLAGS[@]}" "$ROOT/src/breach1999_documented_corrections.f" \
  -o "$ROOT/bin/breach1999_corrected_snan" \
  2> "$ROOT/bin/breach1999_corrected_snan.diagnostics.txt" || true

echo "Built bin/breach1999_reference_snan and bin/breach1999_corrected_snan"
echo "Note: these builds intentionally crash on ANY read of uninitialized"
echo "memory (including in SUBROUTINE PLOT's known-safe F77 idiom -- see"
echo "docs/CHANGE_MATRIX.md), so they are for targeted diagnosis only, not"
echo "for full-run regression. Use bin/breach1999_reference /"
echo "bin/breach1999_corrected for that."
