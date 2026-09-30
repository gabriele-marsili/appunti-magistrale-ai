"""Soluzione di riferimento — Esercizio 04."""
from __future__ import annotations

from itertools import permutations

import numpy as np


def random_instance(rng: np.random.Generator, n: int):
    prop = np.array([rng.permutation(n) for _ in range(n)])
    recv = np.array([rng.permutation(n) for _ in range(n)])
    return prop, recv


def inverti(mu: np.ndarray) -> np.ndarray:
    inv = np.empty_like(mu)
    inv[mu] = np.arange(len(mu))
    return inv


def rank_matrix(prefs: np.ndarray) -> np.ndarray:
    prefs = np.asarray(prefs)
    n = prefs.shape[0]
    R = np.empty((n, prefs.shape[1]), dtype=int)
    righe = np.arange(n)[:, None]
    R[righe, prefs] = np.arange(prefs.shape[1])[None, :]
    return R


def deferred_acceptance(prop_prefs: np.ndarray, recv_prefs: np.ndarray):
    prop_prefs = np.asarray(prop_prefs)
    recv_prefs = np.asarray(recv_prefs)
    n = prop_prefs.shape[0]
    rank_r = rank_matrix(recv_prefs)

    prossima = np.zeros(n, dtype=int)      # indice della prossima proposta
    tenuto = np.full(n, -1, dtype=int)     # tenuto[r] = proponente trattenuto
    liberi = list(range(n))
    n_proposte = 0

    while liberi:
        p = liberi.pop()
        r = int(prop_prefs[p, prossima[p]])
        prossima[p] += 1
        n_proposte += 1
        attuale = tenuto[r]
        if attuale == -1:
            tenuto[r] = p
        elif rank_r[r, p] < rank_r[r, attuale]:
            tenuto[r] = p
            liberi.append(int(attuale))
        else:
            liberi.append(p)

    mu = np.empty(n, dtype=int)
    for r in range(n):
        mu[tenuto[r]] = r
    return mu, n_proposte


def blocking_pairs(mu, prop_prefs, recv_prefs) -> list[tuple[int, int]]:
    mu = np.asarray(mu)
    rank_p = rank_matrix(np.asarray(prop_prefs))
    rank_r = rank_matrix(np.asarray(recv_prefs))
    inv = inverti(mu)
    n = mu.shape[0]
    fuori = []
    for p in range(n):
        for r in range(n):
            if mu[p] == r:
                continue
            if rank_p[p, r] < rank_p[p, mu[p]] and rank_r[r, p] < rank_r[r, inv[r]]:
                fuori.append((p, r))
    return sorted(fuori)


def is_stable(mu, prop_prefs, recv_prefs) -> bool:
    return len(blocking_pairs(mu, prop_prefs, recv_prefs)) == 0


def all_stable_matchings(prop_prefs, recv_prefs) -> list[np.ndarray]:
    n = np.asarray(prop_prefs).shape[0]
    fuori = []
    for perm in permutations(range(n)):
        mu = np.array(perm, dtype=int)
        if is_stable(mu, prop_prefs, recv_prefs):
            fuori.append(mu)
    return fuori


def best_stable_partner(stabili, prop_prefs) -> np.ndarray:
    rank_p = rank_matrix(np.asarray(prop_prefs))
    n = rank_p.shape[0]
    fuori = np.empty(n, dtype=int)
    for p in range(n):
        fuori[p] = min((int(mu[p]) for mu in stabili), key=lambda r: rank_p[p, r])
    return fuori


def worst_stable_partner(stabili, prop_prefs) -> np.ndarray:
    rank_p = rank_matrix(np.asarray(prop_prefs))
    n = rank_p.shape[0]
    fuori = np.empty(n, dtype=int)
    for p in range(n):
        fuori[p] = max((int(mu[p]) for mu in stabili), key=lambda r: rank_p[p, r])
    return fuori
