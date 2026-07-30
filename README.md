# NWS BREACH 1999 — Independent Documented-Corrections Project

This repository preserves the original NWS BREACH (1999) FORTRAN dam-breach
model unmodified, and separately develops an **independent corrected
implementation** based only on publicly documented BRCH 2010 / BRCH 2.0.0
(2018) release descriptions and direct analysis of the 1999 source.

> **This is not the official RiverMechanics BRCH 2.0.0 source code.**
> No RiverMechanics source code was accessed or copied. Exact
> source-level equivalence with BRCH 2.0.0 is not claimed. Call this
> work "*Independent corrected implementation of NWS BREACH 1999 based
> on publicly documented BRCH 2010/2018 corrections*."

## Layout

- `original/` — untouched 1999 source (`SRC/Breach.for`) and example inputs (`Input/*.DAT`). Never edited; SHA-256 hashes in `docs/SOURCE_AUDIT.md`.
- `src/breach1999_reference.f` — byte-identical copy of the original, used for a reproducible baseline build.
- `src/breach1999_documented_corrections.f` — the corrected version. Every change is marked inline with a `C BRCH20xx-DOCFIX-NN:` comment and cross-referenced in `docs/CHANGE_MATRIX.md`.
- `examples/` — copies of the 5 provided example inputs (BSMBOT2, CLAY, LAWN, PERU, TETON).
- `tests/` — build scripts, example/targeted test runners, numeric output comparator.
- `tools/parse_breach_output.py` — parses BREACH stdout into structured JSON.
- `outputs/baseline/`, `outputs/corrected/`, `outputs/targeted/` — saved run outputs for every example and synthetic edge case, both binaries.
- `docs/` — `SOURCE_AUDIT.md`, `VARIABLE_DICTIONARY.md`, `CHANGE_MATRIX.md`, `UNRESOLVED_BRCH2018.md`, `BUILD_AND_RUN.md`, `VALIDATION_REPORT.md`.

## Quick start

```bash
bash tests/build_reference.sh
bash tests/build_corrected.sh
bash tests/run_all_examples.sh bin/breach1999_reference baseline
bash tests/run_all_examples.sh bin/breach1999_corrected corrected
python3 tests/compare_outputs.py outputs/baseline outputs/corrected
bash tests/run_targeted_tests.sh
```

See `docs/BUILD_AND_RUN.md` for details, `docs/CHANGE_MATRIX.md` for what changed and why, and `docs/VALIDATION_REPORT.md` for regression/targeted-test results.
