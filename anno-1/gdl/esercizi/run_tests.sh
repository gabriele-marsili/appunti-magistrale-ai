#!/usr/bin/env bash
# Esegue le suite di tutti gli esercizi.
#
#   ./run_tests.sh          -> testa il TUO codice (gli scheletri che stai riempiendo)
#   ./run_tests.sh --sol    -> testa le soluzioni di riferimento (devono essere tutte verdi)
#   ./run_tests.sh 03 07    -> solo gli esercizi 03 e 07
#
# Uscita 0 se tutto passa, 1 altrimenti.

set -uo pipefail
cd "$(dirname "$0")"

MODE="tuo"
FILTER=()
for arg in "$@"; do
  case "$arg" in
    --sol|-s) MODE="soluzione" ;;
    -h|--help) sed -n '2,10p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) FILTER+=("$arg") ;;
  esac
done

if [ "$MODE" = "soluzione" ]; then export GDL_SOL=1; else unset GDL_SOL; fi

if ! python3 -c "import numpy, pytest" 2>/dev/null; then
  echo "Mancano numpy e/o pytest per questo python3 ($(command -v python3))."
  echo
  echo "  python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
  echo
  echo "oppure attiva il venv che usi per i midterm e rilancia."
  exit 2
fi

ok=0; ko=0; tot_pass=0
printf '%-22s %-10s %s\n' "ESERCIZIO" "ESITO" "DETTAGLIO"
printf '%s\n' "----------------------------------------------------------------"

for dir in [0-9][0-9]_*/; do
  d="${dir%/}"
  if [ ${#FILTER[@]} -gt 0 ]; then
    match=0
    for f in "${FILTER[@]}"; do case "$d" in "$f"*|*"$f"*) match=1 ;; esac; done
    [ $match -eq 1 ] || continue
  fi
  test_file=$(ls "$d"/test_*.py 2>/dev/null | head -1)
  if [ -z "$test_file" ]; then
    printf '%-22s %-10s %s\n' "$d" "SKIP" "nessun test trovato"
    continue
  fi
  out=$(cd "$d" && python3 -m pytest -q --no-header 2>&1)
  summary=$(printf '%s' "$out" | grep -E '[0-9]+ (passed|failed)' | tail -1)
  if printf '%s' "$out" | grep -qE '^[0-9]+ passed'; then
    n=$(printf '%s' "$summary" | grep -oE '^[0-9]+')
    tot_pass=$((tot_pass + n)); ok=$((ok + 1))
    printf '%-22s %-10s %s\n' "$d" "OK" "$summary"
  else
    ko=$((ko + 1))
    printf '%-22s %-10s %s\n' "$d" "DA FARE" "${summary:-errore di import}"
  fi
done

printf '%s\n' "----------------------------------------------------------------"
printf 'modalita: %s | esercizi verdi: %d | da completare: %d | test passati: %d\n' \
  "$MODE" "$ok" "$ko" "$tot_pass"

[ $ko -eq 0 ]
