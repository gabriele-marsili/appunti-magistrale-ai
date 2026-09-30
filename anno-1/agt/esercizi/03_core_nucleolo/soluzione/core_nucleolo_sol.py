"""Soluzione di riferimento — Esercizio 03."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lp import LPInfeasible, lp_min, vertici_ammissibili  # noqa: E402,F401


def coalizioni_proprie(n: int) -> list[int]:
    return [s for s in range(1, (1 << n) - 1)]


def indicatore(s: int, n: int) -> np.ndarray:
    return np.array([1.0 if s >> i & 1 else 0.0 for i in range(n)])


def random_game(rng: np.random.Generator, n: int, lo=0.0, hi=10.0) -> np.ndarray:
    v = rng.uniform(lo, hi, size=1 << n)
    v[0] = 0.0
    return v


def random_superadditive_game(rng: np.random.Generator, n: int) -> np.ndarray:
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
def is_preimputation(v, n, x, tol=1e-7) -> bool:
    x = np.asarray(x, dtype=float)
    return bool(abs(x.sum() - v[(1 << n) - 1]) <= tol)


def is_imputation(v, n, x, tol=1e-7) -> bool:
    x = np.asarray(x, dtype=float)
    if not is_preimputation(v, n, x, tol):
        return False
    return bool(all(x[i] >= v[1 << i] - tol for i in range(n)))


def excess(v, n, x) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    e = np.empty(1 << n)
    for s in range(1 << n):
        e[s] = v[s] - sum(x[i] for i in range(n) if s >> i & 1)
    return e


def theta(v, n, x) -> np.ndarray:
    e = excess(v, n, x)
    propri = np.array([e[s] for s in coalizioni_proprie(n)])
    return np.sort(propri)[::-1]


def lex_leq(a, b, tol=1e-7) -> bool:
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    for u, w in zip(a, b):
        if u < w - tol:
            return True
        if u > w + tol:
            return False
    return True


def in_core(v, n, x, tol=1e-7) -> bool:
    x = np.asarray(x, dtype=float)
    if not is_preimputation(v, n, x, tol):
        return False
    e = excess(v, n, x)
    return bool(all(e[s] <= tol for s in coalizioni_proprie(n)))


def core_vertices(v, n) -> np.ndarray:
    propri = coalizioni_proprie(n)
    A_ub = np.array([-indicatore(s, n) for s in propri])
    b_ub = np.array([-v[s] for s in propri])
    A_eq = np.ones((1, n))
    b_eq = np.array([v[(1 << n) - 1]])
    vert = vertici_ammissibili(A_ub, b_ub, A_eq, b_eq, d=n)
    if vert.shape[0] == 0:
        return np.zeros((0, n))
    return vert


def _lp_min_eps(v, n, libere, eq_A, eq_b):
    """min eps  s.t.  eq,  x(S) + eps >= v(S) per S in libere.  Var: (x, eps)."""
    righe, rhs = [], []
    for s in libere:
        riga = np.concatenate([-indicatore(s, n), [-1.0]])
        righe.append(riga)
        rhs.append(-v[s])
    A_ub = np.array(righe) if righe else np.zeros((0, n + 1))
    b_ub = np.array(rhs) if rhs else np.zeros(0)
    A_eq = np.hstack([np.array(eq_A), np.zeros((len(eq_A), 1))])
    b_eq = np.array(eq_b)
    c = np.concatenate([np.zeros(n), [1.0]])
    return lp_min(c, A_ub, b_ub, A_eq, b_eq)


def _lp_max_xS(v, n, s, libere, eq_A, eq_b, eps_star):
    """max x(S) con eps fissato a eps_star (equivale a min -x(S))."""
    righe, rhs = [], []
    for t in libere:
        righe.append(-indicatore(t, n))
        rhs.append(-(v[t] - eps_star))
    A_ub = np.array(righe) if righe else np.zeros((0, n))
    b_ub = np.array(rhs) if rhs else np.zeros(0)
    A_eq = np.array(eq_A)
    b_eq = np.array(eq_b)
    val, _ = lp_min(-indicatore(s, n), A_ub, b_ub, A_eq, b_eq)
    return -val


def least_core_epsilon(v, n) -> float:
    eq_A = [np.ones(n)]
    eq_b = [v[(1 << n) - 1]]
    eps, _ = _lp_min_eps(v, n, coalizioni_proprie(n), eq_A, eq_b)
    return float(eps)


def nucleolus(v, n, tol=1e-7) -> np.ndarray:
    eq_A = [np.ones(n)]
    eq_b = [float(v[(1 << n) - 1])]
    libere = list(coalizioni_proprie(n))
    x_corrente = None

    while libere:
        eps_star, z = _lp_min_eps(v, n, libere, eq_A, eq_b)
        x_corrente = z[:n]

        fissate = []
        for s in libere:
            massimo = _lp_max_xS(v, n, s, libere, eq_A, eq_b, eps_star)
            if massimo <= v[s] - eps_star + tol:
                fissate.append(s)

        if not fissate:                       # non dovrebbe accadere: salvagente
            break
        for s in fissate:
            eq_A.append(indicatore(s, n))
            eq_b.append(float(v[s] - eps_star))
            libere.remove(s)

        if np.linalg.matrix_rank(np.array(eq_A), tol=1e-9) >= n:
            A = np.array(eq_A)
            b = np.array(eq_b)
            x_corrente = np.linalg.lstsq(A, b, rcond=None)[0]
            break

    return np.asarray(x_corrente, dtype=float)
