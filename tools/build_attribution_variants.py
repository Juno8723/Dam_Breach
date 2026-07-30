#!/usr/bin/env python3
"""Generates the 4 BSMBOT2-attribution source variants (A/B/C/D) described in
docs/BSMBOT2_FIX_ATTRIBUTION.md, by applying isolated patches to a copy of
original/SRC/Breach.for -- never to original/ itself, and never mutating
src/breach1999_documented_corrections.f (the operational corrected source
stays untouched by this script; keeping these two independent toggles
inline in it via #ifdef-style flags was judged to hurt its readability more
than a small standalone generator script does).

Config A: Original          - tailwater fix OFF, time-step fix OFF
Config B: Tailwater only    - tailwater fix ON,  time-step fix OFF
Config C: Time-step only    - tailwater fix OFF, time-step fix ON
Config D: Both              - tailwater fix ON,  time-step fix ON

"Tailwater fix" = BRCH2010-01 + BRCH2010-02 (the two are applied together
since BRCH2010-01's guards read TWD, which BRCH2010-02 changes the initial
value of -- splitting them further isn't meaningful).
"Time-step fix" = BRCH2018-05 (DTH floor + DTHFIL ceiling + steady-state
override).

Verified: none of this project's other corrections (NHSA, NCS, negative-BMX
fallback, AFRA output, reservoir-refill guard, cosmetic formatting) change
BSMBOT2's output at all (confirmed via regression logs from the prior
session), so Configuration D here is expected to match
src/breach1999_documented_corrections.f's actual BSMBOT2 output exactly.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIGINAL = os.path.join(ROOT, "original", "SRC", "Breach.for")
OUTDIR = os.path.join(ROOT, "tests", "attribution", "variants")

TAILWATER_PATCHES = [
    (
        "      TWD=0.\n      TB=0.0",
        "      TWD=HSTW(1)\n      TB=0.0",
    ),
    (
        """      HEAD=HY-PCC
      IF(TWD.GT.0.5*(HC+HPU)) HEAD=HY-TWD
      FNC=1.0+F*CL/HT
      QB=A*SQRT(HEAD)*SQRT(64.4/FNC)
      RN=83333.*QB/A*HT
      IF(RN.GE.2000.) GO TO 72
      FFA=1.
      FFB=0.00077*A*CL/(HT*HT)
      FFC=-64.4*A*A*HEAD
      QB=(-FFB+SQRT(FFB*FFB-4.*FFA*FFC))/(2.*FFA)
   72 S=CN*CN*QB*QB/(2.21*A*A*R**(1.3333))""",
        """      HEAD=HY-PCC
      IF(TWD.GT.0.5*(HC+HPU)) HEAD=HY-TWD
      IF(TWD.GE.HY.OR.HEAD.LE.0.0) THEN
        QB=0.0
        RN=0.0
        HP=0.0
        PPP=HPU
        GO TO 76
      ENDIF
      FNC=1.0+F*CL/HT
      QB=A*SQRT(HEAD)*SQRT(64.4/FNC)
      RN=83333.*QB/A*HT
      IF(RN.GE.2000.) GO TO 72
      FFA=1.
      FFB=0.00077*A*CL/(HT*HT)
      FFC=-64.4*A*A*HEAD
      QB=(-FFB+SQRT(FFB*FFB-4.*FFA*FFC))/(2.*FFA)
   72 S=CN*CN*QB*QB/(2.21*A*A*R**(1.3333))""",
    ),
    (
        """      IF(HR.GT.0.67) SUB=1.0-27.8*(HR-0.67)**3.
      IF(SUB.LT.0.05) SUB=0.05
      IF(SUB.GT.SUBOLD) SUB=SUBOLD
      CV=1.0+0.035*QB*QB/(HD*CRL*CRL*(HY-HL)**2)""",
        """      IF(HR.GT.0.67) SUB=1.0-27.8*(HR-0.67)**3.
      IF(SUB.LT.0.05) SUB=0.05
      IF(SUB.GT.SUBOLD) SUB=SUBOLD
      IF(TWD.GE.HY) SUB=0.0
      CV=1.0+0.035*QB*QB/(HD*CRL*CRL*(HY-HL)**2)""",
    ),
]

TIMESTEP_PATCHES = [
    (
        "  213 DTHFIL=(TQP-TST)/20.\n      DTHFIL=AMIN1(DTHMIN,DTHFIL)\n  210 WRITE(6,9)",
        """  213 DTHFIL=(TQP-TST)/20.
      DTHFIL=AMIN1(DTHMIN,DTHFIL)
      KSTDY=1
      DO 214 K=2,NHP
      IF(ABS(QIN(K)-QIN(1)).GT.0.01*QIN(1)) KSTDY=0
  214 CONTINUE
      IF(KSTDY.EQ.1) DTHFIL=0.5
      IF(DTHFIL.GT.0.5) DTHFIL=0.5
  210 WRITE(6,9)""",
    ),
    (
        "      FK1=PLC/PL\n   22 T=T+DTH",
        "      FK1=PLC/PL\n      IF(DTH.LT.0.0001) DTH=0.0001\n   22 T=T+DTH",
    ),
]


def apply_patches(text, patches, label):
    for old, new in patches:
        n = text.count(old)
        if n != 1:
            print(f"FAIL[{label}]: pattern found {n} times (expected 1):\n{old[:80]}...",
                  file=sys.stderr)
            sys.exit(1)
        text = text.replace(old, new, 1)
    return text


def main():
    with open(ORIGINAL) as f:
        base = f.read()

    os.makedirs(OUTDIR, exist_ok=True)

    configs = {
        "A_original": (False, False),
        "B_tailwater_only": (True, False),
        "C_timestep_only": (False, True),
        "D_both": (True, True),
    }

    for name, (tw, ts) in configs.items():
        text = base
        if tw:
            text = apply_patches(text, TAILWATER_PATCHES, f"{name}/tailwater")
        if ts:
            text = apply_patches(text, TIMESTEP_PATCHES, f"{name}/timestep")
        out_path = os.path.join(OUTDIR, f"breach_{name}.f")
        with open(out_path, "w") as f:
            f.write(text)
        print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
