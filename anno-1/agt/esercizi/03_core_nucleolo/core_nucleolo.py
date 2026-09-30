"""
Esercizio 03 — Core, least core e nucleolo (L20-L23).

Stessa rappresentazione dell'esercizio 02: gioco TU su N = {0,...,n-1} come
array numpy `v` di lunghezza 2**n indicizzato dalla maschera di bit, con v[0]=0.

Il modulo `lp.py` (fornito) risolve LP piccoli per enumerazione dei vertici.
Usalo, non riscriverlo. Vincolo pratico: n <= 4.

Le funzioni con "# TODO" sono da implementare.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lp import LPInfeasible, lp_min, vertici_ammissibili  # noqa: E402,F401


# --------------------------------------------------------------------------
# Codice fornito.
# --------------------------------------------------------------------------
def coalizioni_proprie(n: int) -> list[int]:
    """Maschere delle coalizioni non vuote e diverse da N."""
    return [s for s in range(1, (1 << n) - 1)]


def indicatore(s: int, n: int) -> np.ndarray:
    """Vettore indicatore della coalizione `s`: 1 sulle componenti in S."""
    return np.array([1.0 if s >> i & 1 else 0.0 for i in range(n)])


def random_game(rng: np.random.Generator, n: int, lo=0.0, hi=10.0) -> np.ndarray:
    v = rng.uniform(lo, hi, size=1 << n)
    v[0] = 0.0
    return v


def random_superadditive_game(rng: np.random.Generator, n: int) -> np.ndarray:
    """Gioco superadditivo costruito per chiusura: v(S) = max su bipartizioni."""
    v = np.zeros(1 << n)
    for i in range(n):
        v[1 << i] = rng.uniform(0.0, 3.0)
    for s in range(1, 1 << n):
        if bin(s).count("1") <= 1:
            continue
        base = rng.uniform(0.0, 3.0) + sum(v[1 << i] for i in range(n) if s >> i & 1)
        migliore = base
        t = (s - 1) & s
        while t:
            migliore = max(migliore, v[t] + v[s ^ t])
            t = (t - 1) & s
        v[s] = migliore
    v[0] = 0.0
    return v


def majority_game(n: int) -> np.ndarray:
    """v(S) = 1 se |S| > n/2, 0 altrimenti. Per n dispari ha core vuoto."""
    v = np.array([1.0 if 2 * bin(s).count("1") > n else 0.0 for s in range(1 << n)])
    v[0] = 0.0
    return v


def additive_game(values) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    n = len(values)
    v = np.zeros(1 << n)
    for s in range(1 << n):
        v[s] = sum(values[i] for i in range(n) if s >> i & 1)
    return v


# --------------------------------------------------------------------------
# Da implementare.
# --------------------------------------------------------------------------
def is_preimputation(v: np.ndarray, n: int, x, tol: float = 1e-7) -> bool:
    """Razionalita' SOCIALE (efficienza): x(N) = v(N)."""
    raise NotImplementedError("TODO: is_preimputation")  # TODO


def is_imputation(v: np.ndarray, n: int, x, tol: float = 1e-7) -> bool:
    """Preimputazione + razionalita' INDIVIDUALE: x_i >= v({i}) per ogni i."""
    raise NotImplementedError("TODO: is_imputation")  # TODO


def excess(v: np.ndarray, n: int, x) -> np.ndarray:
    """Vettore degli excess e(S,x) = v(S) - x(S), indicizzato dalla maschera.

    Lunghezza 2**n. e(vuota, x) = 0 e e(N, x) = v(N) - x(N).
    """
    raise NotImplementedError("TODO: excess")  # TODO


def theta(v: np.ndarray, n: int, x) -> np.ndarray:
    """Vettore ORDINATO di insoddisfazione: gli excess delle coalizioni proprie
    (non vuote, diverse da N) in ordine DECRESCENTE.

    Lunghezza 2**n - 2.
    """
    raise NotImplementedError("TODO: theta")  # TODO


def lex_leq(a: np.ndarray, b: np.ndarray, tol: float = 1e-7) -> bool:
    """True se `a` precede o eguaglia `b` nell'ordine lessicografico."""
    raise NotImplementedError("TODO: lex_leq")  # TODO


def in_core(v: np.ndarray, n: int, x, tol: float = 1e-7) -> bool:
    """x sta nel core: x(N) = v(N) e x(S) >= v(S) per ogni S sottoinsieme di N.

    Equivalente: tutti gli excess delle coalizioni proprie sono <= 0.
    """
    raise NotImplementedError("TODO: in_core")  # TODO


def core_vertices(v: np.ndarray, n: int) -> np.ndarray:
    """Vertici del core, come array (k, n). Array vuoto (0, n) se il core e' vuoto.

    Usa `vertici_ammissibili` di lp.py: il core e' definito da 1 uguaglianza
    (x(N) = v(N)) e 2**n - 2 disuguaglianze (-x(S) <= -v(S)).
    """
    raise NotImplementedError("TODO: core_vertices")  # TODO


def least_core_epsilon(v: np.ndarray, n: int) -> float:
    """Il minimo eps tale che lo strong eps-core sia non vuoto (Shapley-Shubik 1966).

        min eps   s.t.   x(N) = v(N),   x(S) >= v(S) - eps  per ogni S proprio

    Il core e' non vuoto se e solo se questo eps e' <= 0.
    Variabili dell'LP: (x_0, ..., x_{n-1}, eps).
    """
    raise NotImplementedError("TODO: least_core_epsilon")  # TODO


def nucleolus(v: np.ndarray, n: int, tol: float = 1e-7) -> np.ndarray:
    """Nucleolo (prenucleolo) del gioco: il punto che minimizza LESSICOGRAFICAMENTE
    theta(x) fra tutte le preimputazioni.

    Schema iterativo di Maschler:
      1. si parte con l'unica uguaglianza x(N) = v(N) e tutte le coalizioni proprie
         "libere";
      2. si risolve  min eps  s.t.  x(S) + eps >= v(S)  per ogni S libera
         (piu' le uguaglianze gia' fissate);
      3. si individuano le coalizioni libere che risultano ATTIVE in OGNI soluzione
         ottima: per ciascuna S si massimizza x(S) tenendo eps = eps*; se il massimo
         vale ancora v(S) - eps*, allora S e' attiva ovunque e si fissa
         l'uguaglianza x(S) = v(S) - eps*;
      4. si rimuovono quelle coalizioni dalle libere e si ripete finche' non
         restano coalizioni libere oppure il punto e' determinato univocamente
         (rango delle uguaglianze pari a n).

    Ritorna un array di lunghezza n.
    """
    raise NotImplementedError("TODO: nucleolus")  # TODO
