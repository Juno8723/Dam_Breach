#!/usr/bin/env bash
# Builds src/breach1999_documented_corrections.f with the
# MASS_BALANCE_DIAGNOSTIC preprocessor flag enabled. This adds a
# diagnostic-only per-timestep mass-balance CSV (mass_balance.csv,
# written to the run's working directory) -- no physical variable,
# computed discharge, elevation, or any existing output is changed.
# See docs/MASS_BALANCE_DIAGNOSTIC.md.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
mkdir -p "$ROOT/bin"

gfortran \
  -std=legacy \
  -ffixed-form \
  -cpp -DMASS_BALANCE_DIAGNOSTIC \
  -O0 \
  -fno-range-check \
  "$ROOT/src/breach1999_documented_corrections.f" \
  -o "$ROOT/bin/breach1999_corrected_massbalance"

echo "Built bin/breach1999_corrected_massbalance"
echo "Running it writes mass_balance.csv to the current directory."
