#!/usr/bin/env bash
# Esegue tutte le suite e stampa un riepilogo.
#   ./run_tests.sh            -> scheletro: TUTTO ROSSO e' il risultato atteso
#   AGT_SOL=1 ./run_tests.sh  -> soluzione: TUTTO VERDE e' il risultato atteso
set -u

QUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="${PYTHON:-python3}"

# ---------------------------------------------------------------------------
# Controllo preliminare dell'ambiente.
# Il venv dei corsi ha numpy (e torch) ma NON ha pytest: senza questo controllo
# si prendono una quindicina di errori di import senza capire perche'.
# ---------------------------------------------------------------------------
manca=""
"$PY" -c "import numpy"  2>/dev/null || manca="$manca numpy"
"$PY" -c "import pytest" 2>/dev/null || manca="$manca pytest"

if [ -n "$manca" ]; then
  echo "ERRORE: mancano questi pacchetti nell'interprete '$PY':$manca"
  echo
  echo "  comando    : $PY"
  echo "  eseguibile : $(command -v "$PY" 2>/dev/null || echo 'NON TROVATO')"
  echo "  VIRTUAL_ENV: ${VIRTUAL_ENV:-non impostato}"
  echo
  echo "Come sistemare."
  echo
  echo "  a) Se stai gia' usando il venv dei corsi, aggiungici solo cio' che manca:"
  echo "       source /percorso/al/venv/bin/activate"
  echo "       pip install$manca"
  echo
  echo "  b) Oppure crea un venv dedicato a questi esercizi:"
  echo "       python3 -m venv .venv"
  echo "       source .venv/bin/activate"
  echo "       pip install -r \"$QUI/requirements.txt\""
  echo
  echo "  c) Oppure indica un altro interprete senza attivare niente:"
  echo "       PYTHON=/percorso/al/venv/bin/python \"$0\""
  echo
  exit 2
fi

if [ "${AGT_SOL:-}" = "1" ]; then
  echo "MODALITA': soluzione di riferimento  (atteso: tutto verde)"
else
  echo "MODALITA': scheletro                 (atteso: tutto rosso)"
fi
"$PY" -c "import numpy, pytest, sys; print('numpy', numpy.__version__, '| pytest', pytest.__version__, '|', sys.executable)"
echo "======================================================================"

nomi=(); esiti=(); passati=(); falliti=()
tot_pass=0; tot_fail=0; suite_ko=0

for dir in "$QUI"/[0-9][0-9]_*/; do
  [ -d "$dir" ] || continue
  nome="$(basename "$dir")"
  echo
  echo ">>> $nome"
  out="$(cd "$dir" && "$PY" -m pytest -q 2>&1)"
  rc=$?
  echo "$out" | tail -n 3
  p=$(echo "$out" | grep -oE '[0-9]+ passed'  | grep -oE '[0-9]+' | tail -n1)
  f=$(echo "$out" | grep -oE '[0-9]+ failed'  | grep -oE '[0-9]+' | tail -n1)
  e=$(echo "$out" | grep -oE '[0-9]+ error'   | grep -oE '[0-9]+' | tail -n1)
  p=${p:-0}; f=${f:-0}; e=${e:-0}
  f=$((f + e))
  nomi+=("$nome"); passati+=("$p"); falliti+=("$f")
  tot_pass=$((tot_pass + p)); tot_fail=$((tot_fail + f))
  if [ "$rc" -ne 0 ]; then suite_ko=$((suite_ko + 1)); esiti+=("KO"); else esiti+=("OK"); fi
done

echo
echo "======================================================================"
printf "%-28s %8s %8s   %s\n" "SUITE" "PASSATI" "FALLITI" "ESITO"
for i in "${!nomi[@]}"; do
  printf "%-28s %8s %8s   %s\n" "${nomi[$i]}" "${passati[$i]}" "${falliti[$i]}" "${esiti[$i]}"
done
echo "----------------------------------------------------------------------"
printf "%-28s %8s %8s\n" "TOTALE" "$tot_pass" "$tot_fail"
echo

if [ "${AGT_SOL:-}" = "1" ]; then
  if [ "$tot_fail" -eq 0 ] && [ "$tot_pass" -gt 0 ]; then
    echo "OK: la soluzione di riferimento passa tutto."
    exit 0
  fi
  echo "PROBLEMA: in modalita' soluzione dovrebbe essere tutto verde."
  exit 1
else
  if [ "$tot_pass" -eq 0 ] && [ "$tot_fail" -gt 0 ]; then
    echo "OK: scheletro tutto rosso, come atteso. Ora implementa le funzioni # TODO."
    exit 0
  fi
  echo "$tot_pass test passano gia' sullo scheletro: se non li hai implementati tu,"
  echo "vuol dire che quei test non toccano nessuna funzione # TODO."
  exit 1
fi
