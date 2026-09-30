"""
Mini solutore LP fornito (NON e' parte dell'esercizio).

Risolve  min c.z  s.t.  A_ub z <= b_ub,  A_eq z = b_eq
per ENUMERAZIONE DEI VERTICI: ogni vertice del poliedro rende attive d = dim(z)
vincoli linearmente indipendenti, quindi si prova ogni combinazione di d righe,
si risolve il sistema quadrato e si tiene il punto se e' ammissibile.

E' esponenziale e va bene solo per i giochi piccoli d'esame (n <= 4), ma e'
esatto e non richiede scipy. La versione batched sfrutta numpy per risolvere
tutti i sistemi in un colpo solo.
"""
from __future__ import annotations

from itertools import combinations

import numpy as np

MAX_COMBINAZIONI = 400_000


class LPInfeasible(Exception):
    """Nessun punto ammissibile."""


def _vertici(A: np.ndarray, b: np.ndarray, d: int) -> np.ndarray:
    m = A.shape[0]
    idx = list(combinations(range(m), d))
    if len(idx) > MAX_COMBINAZIONI:
        raise ValueError(f"troppe combinazioni ({len(idx)}): riduci n")
    idx = np.array(idx, dtype=int)
    M = A[idx]                       # (K, d, d)
    rhs = b[idx]                     # (K, d)
    det = np.linalg.det(M)
    ok = np.abs(det) > 1e-9
    if not ok.any():
        return np.zeros((0, d))
    sol = np.linalg.solve(M[ok], rhs[ok][..., None])   # (K', d, 1)
    return sol[..., 0]


def lp_min(c, A_ub=None, b_ub=None, A_eq=None, b_eq=None, tol: float = 1e-7):
    """Ritorna ``(valore_ottimo, z_ottimo)``. Solleva `LPInfeasible` se vuoto.

    Assume che l'ottimo sia attinto in un vertice (vero per i poliedri puntati
    usati in questo esercizio).
    """
    c = np.asarray(c, dtype=float)
    d = c.shape[0]

    blocchi_A, blocchi_b = [], []
    if A_ub is not None and len(A_ub):
        blocchi_A.append(np.asarray(A_ub, dtype=float))
        blocchi_b.append(np.asarray(b_ub, dtype=float))
    if A_eq is not None and len(A_eq):
        blocchi_A.append(np.asarray(A_eq, dtype=float))
        blocchi_b.append(np.asarray(b_eq, dtype=float))
    A = np.vstack(blocchi_A)
    b = np.concatenate(blocchi_b)

    cand = _vertici(A, b, d)
    if cand.shape[0] == 0:
        raise LPInfeasible("nessun vertice")

    ok = np.ones(cand.shape[0], dtype=bool)
    if A_ub is not None and len(A_ub):
        Au = np.asarray(A_ub, dtype=float)
        bu = np.asarray(b_ub, dtype=float)
        ok &= np.all(cand @ Au.T <= bu + tol, axis=1)
    if A_eq is not None and len(A_eq):
        Ae = np.asarray(A_eq, dtype=float)
        be = np.asarray(b_eq, dtype=float)
        ok &= np.all(np.abs(cand @ Ae.T - be) <= tol, axis=1)

    amm = cand[ok]
    if amm.shape[0] == 0:
        raise LPInfeasible("nessun vertice ammissibile")
    valori = amm @ c
    j = int(np.argmin(valori))
    return float(valori[j]), amm[j]


def vertici_ammissibili(A_ub=None, b_ub=None, A_eq=None, b_eq=None,
                        d: int | None = None, tol: float = 1e-7) -> np.ndarray:
    """Tutti i vertici ammissibili del poliedro (deduplicati, ordinati)."""
    blocchi_A, blocchi_b = [], []
    if A_ub is not None and len(A_ub):
        blocchi_A.append(np.asarray(A_ub, dtype=float))
        blocchi_b.append(np.asarray(b_ub, dtype=float))
    if A_eq is not None and len(A_eq):
        blocchi_A.append(np.asarray(A_eq, dtype=float))
        blocchi_b.append(np.asarray(b_eq, dtype=float))
    A = np.vstack(blocchi_A)
    b = np.concatenate(blocchi_b)
    if d is None:
        d = A.shape[1]

    cand = _vertici(A, b, d)
    if cand.shape[0] == 0:
        return np.zeros((0, d))

    ok = np.ones(cand.shape[0], dtype=bool)
    if A_ub is not None and len(A_ub):
        Au = np.asarray(A_ub, dtype=float)
        bu = np.asarray(b_ub, dtype=float)
        ok &= np.all(cand @ Au.T <= bu + tol, axis=1)
    if A_eq is not None and len(A_eq):
        Ae = np.asarray(A_eq, dtype=float)
        be = np.asarray(b_eq, dtype=float)
        ok &= np.all(np.abs(cand @ Ae.T - be) <= tol, axis=1)
    amm = cand[ok]
    if amm.shape[0] == 0:
        return np.zeros((0, d))
    arrotondati = np.round(amm, 7)
    _, unici = np.unique(arrotondati, axis=0, return_index=True)
    return amm[np.sort(unici)]
