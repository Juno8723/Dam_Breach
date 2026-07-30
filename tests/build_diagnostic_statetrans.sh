#!/usr/bin/env bash
# Builds src/breach1999_documented_corrections.f with the
# STATE_TRANSITION_DIAGNOSTIC preprocessor flag enabled. This adds a
# diagnostic-only KG/KREG state-transition log (state_transitions.csv,
# written to the run's working directory) -- no physical variable or
# any existing output is changed. See docs/STATE_TRANSITION_DIAGNOSTIC.md.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
mkdir -p "$ROOT/bin"

gfortran \
  -std=legacy \
  -ffixed-form \
  -cpp -DSTATE_TRANSITION_DIAGNOSTIC \
  -O0 \
  -fno-range-check \
  "$ROOT/src/breach1999_documented_corrections.f" \
  -o "$ROOT/bin/breach1999_corrected_statetrans"

echo "Built bin/breach1999_corrected_statetrans"
echo "Running it writes state_transitions.csv to the current directory."
