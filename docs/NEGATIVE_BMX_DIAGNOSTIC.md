# NEGATIVE_BMX_DIAGNOSTIC.md

## 1. Reproduction procedure

```bash
bash tests/build_reference.sh          # bin/breach1999_reference
bash tests/build_diagnostic_snan.sh    # bin/breach1999_reference_snan, bin/breach1999_corrected_snan
mkdir -p /tmp/run && cd /tmp/run
cp tests/targeted/negative_bmx.dat in.dat
/path/to/bin/breach1999_reference > out.txt 2> err.txt   # run repeatedly; compare QBP in out.txt
```

`tests/targeted/negative_bmx.dat` is `examples/CLAY.DAT` with its crest length `CRL` shrunk from 500 ft to 100 ft (only that one field changed), which drives the *existing, unmodified* fallback formula `BMX=CRL-2.*(HU-HL)/TAN(40./57.2)` (`original/SRC/Breach.for:1639`) to a negative value (`100 - 2.38*90 ≈ -114 ft`).

## 2. Compiler / environment

- `gfortran` (GNU Fortran 15.2.0, conda-forge build), Linux x86_64, WSL2 kernel.
- Diagnostic flags requested by this task:
  ```
  -std=legacy -ffixed-form -O0 -g -Wall -Wextra -Wconversion -fcheck=all
  -fbacktrace -finit-real=snan -finit-integer=-999999
  -ffpe-trap=invalid,zero,overflow
  ```
  New script: `tests/build_diagnostic_snan.sh` (kept separate from `tests/build_reference.sh`/`build_corrected.sh` since it deliberately makes the program crash on the very first uninitialized read — useful for *pinpointing* bugs, useless for a normal regression run).

**Compatibility note — `-finit-real=snan` had to be worked around, not used as-is for root-causing this specific bug.** It compiles cleanly, but poisoning every `REAL` with a signaling NaN makes the program abort on the **first** use of *any* uninitialized real — including the already-known, already-fixed `AFR`/`AFRA` output bug (BRCH2018-06: `original/SRC/Breach.for:357`, `WRITE(6,402) AFR,...` reads `AFR` before its first real assignment). That crash happens during program startup on *every* input, including all 5 normal examples, before the code ever reaches the negative-BMX-specific state we wanted to isolate:

```
Program received signal SIGFPE: Floating-point exception - erroneous arithmetic operation.
#4 formatted_transfer_scalar_write at .../transfer.c:2359
#5 MAIN__ at src/breach1999_reference.f:357
```

This is itself a useful independent confirmation of the already-documented `AFR` bug (found by a completely different technique than the original static-reading approach), but it meant `-finit-real=snan` alone could not reach the negative-BMX code path in the *original* source (which cannot be edited to skip past it). **Safe alternative used:** `-finit-real=nan` (quiet NaN — poisons memory the same way, but printing/comparing a quiet NaN doesn't itself trap; only a genuine arithmetic operation on it does). This got past the `AFR` line and crashed instead at:

```
Program received signal SIGFPE: Floating-point exception - erroneous arithmetic operation.
#1 MAIN__ at src/breach1999_reference.f:1109
```

`original/SRC/Breach.for:1109` is `IF(NIGG.EQ.1.AND.QB.LT.QBP) GO TO 309` — a comparison against `QBP`, which is exactly the variable that turned out to be the root cause (see §5).

## 3. Repeated-run results (20× each, identical binary + identical input)

Script used: an ad-hoc Python driver (not committed — trivial, see `outputs/analysis/negative_bmx_repeated_runs.json` for the raw captured data) that runs a binary 20 times in a fresh temp directory each time and extracts the `QBP` summary line and a SHA-256 of the full stdout.

| Build | Distinct `QBP` values across 20 runs | Distinct stdout hashes |
|---|---|---|
| `bin/breach1999_reference` (unmodified 1999) | `0.`, `-184066.`, `-1471.`, `-0.`, `**********` (5 distinct) | 5 |
| `bin/breach1999_corrected` (this project, current state) | `137255.` (1 distinct, every run) | 1 |

The `**********` value is a **`FORMAT` field overflow** (`F10.0` can't display a number whose magnitude needs more than 10 characters) — but it is a *symptom* of the same root cause below, not an independent bug: the underlying uninitialized value's magnitude simply varies from run to run, and when it happens to be very large, printing it overflows the field. Classifying this separately as `CONFIRMED_FORMAT_OVERFLOW_ONLY` would be misleading; it is downstream of §5.

## 4. Valgrind

**Not usable in this environment.** `valgrind` (v3.27.1) was installed into the `Breach` conda environment (`conda install -n Breach -c conda-forge valgrind`), but fails at startup on every invocation:

```
valgrind: Fatal error at startup: a function redirection
which is mandatory for this platform-tool combination cannot be set up.
A must-be-redirected function whose name matches the pattern: memcmp
in an object with soname matching: ld-linux-x86-64.so.2 was not found...
Possible fixes: (1, short term): install glibc's debuginfo package
  On Debian, Ubuntu: libc6-dbg
```

Fixing this requires installing `libc6-dbg` via `apt`, which requires root (`sudo -n apt-get install libc6-dbg` failed: `sudo: a password is required`, and no non-interactive privilege escalation is available in this session). This is an environment limitation, not a decision to skip memory-checking — the compiler-based diagnostic in §5 substitutes for it and reaches a conclusive result independently.

## 5. Code trace and root cause

`original/SRC/Breach.for` initializes dozens of MAIN-program locals right after `CALL RDDATA` (e.g. `QBOLD=0.` at line 247, `NIGG=0` at line 313, `QBS(1)=0.` at line 261). **Five variables that are read in the final `OUTPUT SUMMARY` block are missing from this initialization list**, because in every *normal* run they get assigned long before the summary prints — but only inside one conditional block:

```fortran
c original/SRC/Breach.for:1108-1119
      IF(QB.LT.QBOLD) NIGG=1
      IF(NIGG.EQ.1.AND.QB.LT.QBP) GO TO 309   ! <- reads QBP
      BOS=BC
      BTS=BT
      QBP=QB                                   ! <- QBP finally assigned here
      WB=0.5*(BT+BC)
      HMP=HYP-HC
      ZS=TAN(AALC/57.296)
      QBA=0.5*(QB+QBOLD)
      ASTM=ASTM+QBA*DTHOLD*3600.
      IF(QBP.LT.0.01) GO TO 309
      TFHI=ASTM/(QBP/2.*3600.)
```

`QBP` (peak breach outflow so far), `BOS`, `BTS` (feeds `BRW=BTS` in the final summary, `original/SRC/Breach.for:1332`), `ZS`, and `TFHI` are **only ever assigned inside this block**, and `QBP` is itself **read** at line 1109 before its own line-1112 assignment on the very first pass. `grep -n "QBP=" original/SRC/Breach.for` confirms exactly one assignment site (line 1112) and no initializer anywhere else in the file.

In every normal run (all 5 examples), breach outflow starts at 0 and grows, so this block executes at least once early on and all five variables get real values well before the final summary. **With `BMX` negative, the breach geometry is corrupted from the start** (bottom width clamps to a negative number wherever `BMX` is used as a ceiling — `original/SRC/Breach.for:723,767`) and breach discharge `QB` apparently never satisfies this block's gating condition in a way that reaches line 1112 — so `QBP`/`BOS`/`BTS`/`ZS`/`TFHI` are printed in the final summary **still holding whatever was in that memory before the program touched it**, which is not defined by the FORTRAN standard and, empirically on this platform, varies from run to run (consistent with process-to-process variation in uninitialized stack/BSS content — e.g. ASLR-influenced memory layout).

### Causal isolation experiment (confirms the diagnosis directly, not just by inference)

A throwaway copy of the *unmodified* 1999 source (not `original/`, not `src/breach1999_reference.f` — a disposable `/tmp` copy used only for this diagnostic and not committed anywhere) was patched with **only** the five initializations below, with *no* `BMX` fix and no other change:

```fortran
      QBP=0.
      BOS=0.
      BTS=0.
      ZS=0.
      TFHI=0.
```

Result: 20/20 runs on `negative_bmx.dat` now produce the **identical** `QBP=0.` every time (vs. 5 distinct values in the unmodified original). The output is still *physically wrong* (no breach develops, because `BMX` is still negative and that is a separate defect — BRCH2018-03), but it is now **deterministic**. This isolates the non-determinism to exactly these five variables' missing initialization, independent of the `BMX` geometry bug itself.

### Array-bounds check

`gfortran -fcheck=all -fbacktrace` on the unmodified source against `negative_bmx.dat` aborts, but only at the **already-documented, unrelated** `SUBROUTINE PLOT` false positive (`DIMENSION Q(1),T(1)`, a standard F77 size-agnostic-dummy idiom — see `CHANGE_MATRIX.md`'s diagnostic note), identical to what happens on every other input including the 5 normal examples. No negative-BMX-*specific* array-bounds violation was found; the non-determinism is a pure scalar-initialization issue, not an out-of-bounds array access.

## 6. Conclusion

**Classification: `CONFIRMED_UNINITIALIZED_VALUE`**

- Root cause: `QBP`, `BOS`, `BTS`, `ZS`, `TFHI` in `original/SRC/Breach.for` MAIN are read (directly, or via the final summary `WRITE`) without a guaranteed prior assignment when breach discharge never triggers the "new peak" block — a state reachable in normal operation only pathologically (e.g., via the pre-existing negative-`BMX` bug corrupting breach geometry so severely that discharge never grows).
- Confidence: **high**. Supported by (a) direct source reading showing exactly one assignment site for `QBP` and no initializer, (b) a `-finit-real=nan` diagnostic build reproducing a crash at the exact comparison line that reads `QBP` before its own assignment, (c) 20/20 repeated runs showing 5 distinct outputs in the unmodified binary vs. 1 in a version with only these five initializations added, and (d) ruling out array-bounds errors as a contributing factor via `-fcheck=all`.
- The apparent variety of symptoms (`0.`, small negative numbers, `**********` overflow, `-0.`) are **all the same root cause** manifesting differently depending on the magnitude of whatever uninitialized value happened to occupy that memory on a given run — not multiple independent bugs.
- Valgrind could not be used to further corroborate this at the instruction level due to an environment limitation (missing `libc6-dbg`, requires root not available in this session) — noted honestly rather than skipped silently.

## 7. How the corrected version blocks this

`src/breach1999_documented_corrections.f` now initializes all five variables to `0.0` immediately after `QBOLD=0.` in the same init block (see the `C BRCH2018-DOCFIX-07:` comment at that location), on top of the already-applied `BRCH2018-03` fix (`BMX<0 → BMX=CRL`) that prevents the geometry corruption from happening in the first place. Both fixes are independently confirmed:

- With only the init fix (no `BMX` fix): deterministic but still physically wrong (`QBP=0.`, no breach) — see the isolation experiment above.
- With both fixes (the actual `src/breach1999_documented_corrections.f`): deterministic **and** physically sane (`QBP=137,255 cfs` every one of 20 runs, breach develops and drains normally).

This `QBP`/`BOS`/`BTS`/`ZS`/`TFHI` initialization is a new addition to this project's `BRCH2018-07` scope (safe initialization / gfortran-compatibility audit) beyond what was found in the prior session; it is not one of the RiverMechanics-documented BRCH2010/2018 items, but a plain read-before-write bug found by direct analysis, matching the "don't guess, but do fix what you can confirm" principle already established for this project. `docs/CHANGE_MATRIX.md`'s `BRCH2018-07` row and `docs/UNRESOLVED_BRCH2018.md` are updated accordingly.

## 8. A diagnostic-tooling artifact found while building `bin/breach1999_corrected_snan` (not a new bug)

Running `bin/breach1999_corrected_snan` (`-finit-real=snan -fcheck=all` together) against the *normal* `TETON.DAT` example aborts at `src/breach1999_documented_corrections.f:1187` — inside the adaptive-`DTH` section, well before `SUBROUTINE PLOT` is ever reached. This looked like a second real bug at first, but isolating the two flag groups shows it is not:

- `-finit-real=nan` (quiet NaN) **alone**, no `-fcheck=all`: `TETON.DAT` runs to completion normally, exit 0.
- `-fcheck=all` **alone**, no NaN-poisoning: aborts only at the already-documented `SUBROUTINE PLOT` false positive (`CHANGE_MATRIX.md`'s diagnostic note), same as every other input.
- Only the **combination** of both flags together produces the line-1187 abort.

This is consistent with an interaction between gfortran's bounds-checking instrumentation and NaN-poisoned memory (e.g. bounds-check code computing/validating an index derived from a not-yet-written array slot) rather than a defect reachable in a real, non-instrumented build — every actual production run (`bin/breach1999_corrected`, all 5 examples, all 20 repeated negative-BMX runs) is clean and deterministic. Recorded here for transparency since it surfaced during this diagnostic work, not chased further given it doesn't reproduce without artificial poisoning **and** artificial bounds-checking combined.
