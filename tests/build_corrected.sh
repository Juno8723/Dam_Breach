#!/usr/bin/env bash
# Builds the independent documented-corrections binary from
# src/breach1999_documented_corrections.f. This is NOT official
# RiverMechanics BRCH 2.0.0 — see README.md.
#
# -cpp is required because the source contains #ifdef-guarded diagnostic
# blocks (MASS_BALANCE_DIAGNOSTIC, STATE_TRANSITION_DIAGNOSTIC -- see
# tests/build_diagnostic_massbalance.sh / build_diagnostic_statetrans.sh).
# With no -D flags (as here), every guarded block is compiled out and the
# resulting binary's physics/output is identical to a build without -cpp.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
mkdir -p "$ROOT/bin"

gfortran \
  -std=legacy \
  -ffixed-form \
  -cpp \
  -O0 \
  -fno-range-check \
  "$ROOT/src/breach1999_documented_corrections.f" \
  -o "$ROOT/bin/breach1999_corrected"

gfortran \
  -std=legacy \
  -ffixed-form \
  -cpp \
  -O0 \
  -Wall \
  -Wextra \
  -Wconversion \
  -fcheck=all \
  -fbacktrace \
  -ffpe-trap=invalid,zero,overflow \
  "$ROOT/src/breach1999_documented_corrections.f" \
  -o "$ROOT/bin/breach1999_corrected_debug" \
  2> "$ROOT/bin/breach1999_corrected_debug.diagnostics.txt" || true

echo "Built bin/breach1999_corrected and bin/breach1999_corrected_debug"
