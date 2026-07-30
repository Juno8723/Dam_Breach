#!/usr/bin/env bash
# Bash counterpart to run_timestep_convergence.py (kept as the actual
# runner since repeated python subprocess.run() calls in this environment
# were intermittently hanging on unrelated variants; plain shell `timeout`
# proved reliable throughout this project). Produces the same CSV shape.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BIN_DIR="$ROOT/bin/timestep_variants"
OUT_CSV="$ROOT/outputs/analysis/timestep_convergence.csv"
STDOUT_DIR="$ROOT/outputs/analysis/timestep_stdout"
mkdir -p "$ROOT/outputs/analysis" "$STDOUT_DIR"

DATASETS=(BSMBOT2 TETON CLAY)
declare -A SWEEP=(
  [dth_1p0em3]="dth_floor,1.0e-3" [dth_5p0em4]="dth_floor,5.0e-4"
  [dth_1p0em4]="dth_floor,1.0e-4" [dth_5p0em5]="dth_floor,5.0e-5"
  [dth_1p0em5]="dth_floor,1.0e-5"
  [dthfil_1p0]="dthfil_ceiling,1.0" [dthfil_0p5]="dthfil_ceiling,0.5"
  [dthfil_0p25]="dthfil_ceiling,0.25" [dthfil_0p1]="dthfil_ceiling,0.1"
)

echo "sweep,value,dataset,exit_code,completed,runtime_sec,stdout_lines,QBP,QP,TP,HY_final,BO_final,BRD,TFH,TFHI" > "$OUT_CSV"

for tag in dth_1p0em3 dth_5p0em4 dth_1p0em4 dth_5p0em5 dth_1p0em5 dthfil_1p0 dthfil_0p5 dthfil_0p25 dthfil_0p1; do
  IFS=',' read -r sweep value <<< "${SWEEP[$tag]}"
  bin="$BIN_DIR/$tag"
  for ds in "${DATASETS[@]}"; do
    d="$(mktemp -d)"
    cp "$ROOT/examples/$ds.DAT" "$d/in.dat"
    t0=$(date +%s.%N)
    (cd "$d" && timeout 30 "$bin" > stdout.txt 2> stderr.txt)
    code=$?
    t1=$(date +%s.%N)
    elapsed=$(echo "$t1 - $t0" | bc)
    nlines=$(wc -l < "$d/stdout.txt")
    json="$(python3 "$ROOT/tools/parse_breach_output.py" "$d/stdout.txt" --no-hydrograph 2>/dev/null)"
    read -r qbp qp tp hyf bof brd tfh tfhi completed <<< "$(python3 - "$json" <<'PYEOF'
import json, sys
try:
    d = json.loads(sys.argv[1])
except Exception:
    d = {"completed": False, "summary": {}}
s = d.get("summary", {})
vals = [s.get(k) for k in ("QBP","QP","TP","HY_final","BO_final","BRD","TFH","TFHI")]
print(*[v if v is not None else "NA" for v in vals], d.get("completed", False))
PYEOF
)"
    echo "$sweep,$value,$ds,$code,$completed,$elapsed,$nlines,$qbp,$qp,$tp,$hyf,$bof,$brd,$tfh,$tfhi" >> "$OUT_CSV"
    echo "[$tag] $ds: exit=$code QBP=$qbp HY_final=$hyf t=${elapsed}s lines=$nlines"
    cp "$d/stdout.txt" "$STDOUT_DIR/${sweep}_${value}_${ds}.stdout.txt"
    rm -rf "$d"
  done
done
echo "wrote $OUT_CSV"
