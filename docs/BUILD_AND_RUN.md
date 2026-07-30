# BUILD_AND_RUN.md

## Requirements

- `gfortran` (any recent version; developed against GNU Fortran 15.2.0, conda-forge build)
- `python3` (for `tools/parse_breach_output.py` and `tests/compare_outputs.py`, standard library only)

## Directory layout

```
original/         untouched NWS BREACH 1999 source + example inputs (never edit)
src/
  breach1999_reference.f              byte-identical copy of original/SRC/Breach.for
  breach1999_documented_corrections.f independent documented-corrections version
examples/         example .dat inputs (copies of original/Input/*.DAT)
tests/
  build_reference.sh                  compiles src/breach1999_reference.f
  build_corrected.sh                  compiles src/breach1999_documented_corrections.f
  run_all_examples.sh <bin> <label>   runs every examples/*.DAT through a binary
  targeted/*.dat                      hand-built synthetic edge-case inputs
tools/parse_breach_output.py          parses BREACH stdout into JSON
outputs/
  baseline/    reference-binary output for each example
  corrected/   corrected-binary output for each example
  targeted/    reference vs. corrected output for each targeted case
bin/            compiled executables (gitignored)
```

## Building

```bash
bash tests/build_reference.sh
# -> bin/breach1999_reference        (unmodified 1999 logic, -O0, clean)
# -> bin/breach1999_debug            (same source, -Wall -Wextra -Wconversion
#                                      -fcheck=all -fbacktrace -ffpe-trap=...)
# -> bin/breach1999_debug.diagnostics.txt   (compiler warnings from the debug build)

bash tests/build_corrected.sh
# -> bin/breach1999_corrected
# -> bin/breach1999_corrected_debug
```

Both scripts use `-std=legacy -ffixed-form` (fixed-form FORTRAN 77) and `-fno-range-check` for the optimized build. No source-level changes were needed to get a clean compile of the unmodified 1999 source.

**Note on the debug build:** `bin/breach1999_debug`/`bin/breach1999_corrected_debug` (`-fcheck=all`) will abort with an array-bounds error inside `SUBROUTINE PLOT` on *every* input — this is a known false positive from a standard F77 "dummy array declared as size 1" idiom (`DIMENSION Q(1),T(1)`), not a real bug. See `CHANGE_MATRIX.md`'s diagnostic-note section. Use the debug build only to read compile-time warnings, not for full runs; use the plain (non-`-fcheck`) binaries for actual regression runs.

## Running one case by hand

BREACH reads from a hardcoded filename `in.dat` in the current directory and writes its report to stdout:

```bash
mkdir -p /tmp/run && cd /tmp/run
cp /path/to/examples/TETON.DAT in.dat
/path/to/bin/breach1999_corrected > out.txt 2> err.txt
```

Unit 0 (stderr) only ever receives one line (the `BREACH MODEL,VERSION: 07/88-1` banner, `original/SRC/Breach.for:168`) plus any gfortran runtime notes (e.g. floating-point exception flags). Everything else — including the detailed per-timestep table and the final summary/hydrograph plot — goes to unit 6 (stdout). Don't redirect both into one file with `2>&1` if you need to parse stdout programmatically: gfortran buffers unit 6 but not unit 0, so the single stderr line can appear to "jump" into the middle of the stdout content when merged — a cosmetic interleaving artifact, not a real ordering bug (see the discussion earlier in this project's history).

## Running all examples / parsing output

```bash
bash tests/run_all_examples.sh bin/breach1999_reference baseline
bash tests/run_all_examples.sh bin/breach1999_corrected corrected
```

Each writes `outputs/<label>/<CASE>.{stdout,stderr,exitcode,parsed.json}.txt` for every `examples/*.DAT`.

`tools/parse_breach_output.py` extracts: the `OUTPUT SUMMARY` block (`QBP, TP, QP, TRS, TB, BRD, BRW, HU, HY_final, HC_final, AGL, QO, Z, TFH, TFHI, BO_final`), the full per-timestep hydrograph when `DBG` is high enough to print it (`I, T, DTH, KREG, KCOL, QTOT, QTS, QB, SUB, BT, HY, HC, BC, PPP, HP, TWD, DH, DHH, KIT, AGL`), and `KREG` transition points. Run it standalone: `python3 tools/parse_breach_output.py path/to/stdout.txt`.

## Comparing reference vs. corrected

```bash
python3 tests/compare_outputs.py outputs/baseline outputs/corrected
```

See `VALIDATION_REPORT.md` for the tolerance used and why.

## Targeted (synthetic edge-case) tests

```bash
bash tests/run_targeted_tests.sh
```

Runs every `tests/targeted/*.dat` through both binaries and reports pass/fail per the expectations documented in `VALIDATION_REPORT.md`.
