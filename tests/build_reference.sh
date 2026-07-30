#!/usr/bin/env bash
# Builds the unmodified NWS BREACH 1999 reference binary (and a diagnostics
# build with the same source) from src/breach1999_reference.f.
# No calculation logic is changed by this script or by the source it compiles.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
mkdir -p "$ROOT/bin"

gfortran \
  -std=legacy \
  -ffixed-form \
  -O0 \
  -fno-range-check \
  "$ROOT/src/breach1999_reference.f" \
  -o "$ROOT/bin/breach1999_reference"

gfortran \
  -std=legacy \
  -ffixed-form \
  -O0 \
  -Wall \
  -Wextra \
  -Wconversion \
  -fcheck=all \
  -fbacktrace \
  -ffpe-trap=invalid,zero,overflow \
  "$ROOT/src/breach1999_reference.f" \
  -o "$ROOT/bin/breach1999_debug" \
  2> "$ROOT/bin/breach1999_debug.diagnostics.txt" || true

echo "Built bin/breach1999_reference and bin/breach1999_debug"
echo "Debug-build diagnostics: bin/breach1999_debug.diagnostics.txt"
