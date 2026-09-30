"""
Esercizio 02 — Valore di Shapley, assiomi e indici di potere (L24).

Rappresentazione di un gioco TU (N, v) con N = {0, ..., n-1}:
un array numpy `v` di lunghezza 2**n, indicizzato dalla MASCHERA di bit della
coalizione. Il bit i vale 1 se il giocatore i sta nella coalizione.
Quindi `v[0] == 0` (coalizione vuota) e `v[(1 << n) - 1] == v(N)`.

Le funzioni con "# TODO" sono da implementare.
"""
from __future__ import annotations

from itertools import permutations

import numpy as np


# --------------------------------------------------------------------------
# Codice fornito.
# --------------------------------------------------------------------------
def mask_of(players) -> int:
    """Maschera di bit di una collezione di giocatori. `mask_of([0, 2]) == 5`."""
    mask = 0
    for i in players:
        mask |= 1 << i
    return mask


def players_of(mask: int, n: int) -> list[int]:
    """Lista dei giocatori nella coalizione `mask`."""
    return [i for i in range(n) if mask >> i & 1]


def random_game(rng: np.random.Generator, n: int, lo: float = 0.0,
                hi: float = 10.0) -> np.ndarray:
    """Gioco TU casuale con v(vuota) = 0. Deterministico dato `rng`."""
    v = rng.uniform(lo, hi, size=1 << n)
    v[0] = 0.0
    return v


def unanimity_game(n: int, T) -> np.ndarray:
    """Gioco di unanimita' u_T: u_T(S) = 1 se T subseteq S, 0 altrimenti."""
    t = mask_of(T)
    v = np.zeros(1 << n)
    for s in range(1 << n):
        if s & t == t:
            v[s] = 1.0
    v[0] = 0.0
    return v


def additive_game(values) -> np.ndarray:
    """Gioco additivo: v(S) = sum_{i in S} values[i]."""
    values = np.asarray(values, dtype=float)
    n = len(values)
    v = np.zeros(1 << n)
    for s in range(1 << n):
        v[s] = sum(values[i] for i in range(n) if s >> i & 1)
    return v


# --------------------------------------------------------------------------
# Da implementare.
# --------------------------------------------------------------------------
def shapley_marginal(v: np.ndarray, n: int) -> np.ndarray:
    """Valore di Shapley con la FORMULA dei contributi marginali pesati.

        Sh_i(v) = sum_{S subseteq N \\ {i}}  |S|! (n-|S|-1)! / n!  [ v(S u {i}) - v(S) ]

    Iterare sulle 2**(n-1) coalizioni che NON contengono i. Usare `math.factorial`
    (o i pesi precalcolati) e non passare per le permutazioni: quella e' l'altra
    funzione, e i due conti devono restare indipendenti.
    """
    raise NotImplementedError("TODO: shapley_marginal")  # TODO


def shapley_permutations(v: np.ndarray, n: int) -> np.ndarray:
    """Valore di Shapley come MEDIA sulle n! permutazioni (forza bruta).

    Per ogni ordine di arrivo dei giocatori, ciascuno incassa il proprio
    contributo marginale alla coalizione dei predecessori; si media sulle n!
    permutazioni. Praticabile fino a n = 7 (5040 permutazioni).

    Questa e' la definizione "operativa" del valore di Shapley e fa da oracolo
    indipendente per `shapley_marginal`.
    """
    raise NotImplementedError("TODO: shapley_permutations")  # TODO


def banzhaf_raw(v: np.ndarray, n: int) -> np.ndarray:
    """Indice di Banzhaf grezzo (non normalizzato).

        Bz_i(v) = (1 / 2**(n-1)) * sum_{S subseteq N \\ {i}} [ v(S u {i}) - v(S) ]

    Stessa somma di Shapley ma con pesi UNIFORMI invece che pesati per |S|.
    In generale NON e' efficiente: sum_i Bz_i(v) != v(N).
    """
    raise NotImplementedError("TODO: banzhaf_raw")  # TODO


def banzhaf_normalized(v: np.ndarray, n: int) -> np.ndarray:
    """Indice di Banzhaf normalizzato: Bz_i / sum_j Bz_j."""
    raise NotImplementedError("TODO: banzhaf_normalized")  # TODO


def weighted_voting_game(weights, quota: float) -> np.ndarray:
    """Gioco di voto pesato [q; w_1, ..., w_n]: v(S) = 1 se w(S) >= q, 0 altrimenti.

    E' un gioco semplice (valori in {0,1}), monotono, con v(vuota) = 0.
    """
    raise NotImplementedError("TODO: weighted_voting_game")  # TODO


def shapley_shubik(weights, quota: float) -> np.ndarray:
    """Indice di potere di Shapley-Shubik del gioco di voto pesato [q; w].

    E' il valore di Shapley del gioco semplice corrispondente: la frazione di
    permutazioni in cui il giocatore i e' il PIVOT, cioe' quello il cui ingresso
    fa passare la coalizione da perdente a vincente.
    """
    raise NotImplementedError("TODO: shapley_shubik")  # TODO


def is_null_player(v: np.ndarray, n: int, i: int, tol: float = 1e-9) -> bool:
    """True se v(S u {i}) == v(S) per ogni S che non contiene i."""
    raise NotImplementedError("TODO: is_null_player")  # TODO


def are_symmetric(v: np.ndarray, n: int, i: int, j: int, tol: float = 1e-9) -> bool:
    """True se v(S u {i}) == v(S u {j}) per ogni S che non contiene ne' i ne' j."""
    raise NotImplementedError("TODO: are_symmetric")  # TODO
