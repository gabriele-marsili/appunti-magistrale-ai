"""Soluzione di riferimento — Esercizio 02."""
from __future__ import annotations

from itertools import permutations
from math import factorial

import numpy as np


def mask_of(players) -> int:
    mask = 0
    for i in players:
        mask |= 1 << i
    return mask


def players_of(mask: int, n: int) -> list[int]:
    return [i for i in range(n) if mask >> i & 1]


def random_game(rng: np.random.Generator, n: int, lo: float = 0.0,
                hi: float = 10.0) -> np.ndarray:
    v = rng.uniform(lo, hi, size=1 << n)
    v[0] = 0.0
    return v


def unanimity_game(n: int, T) -> np.ndarray:
    t = mask_of(T)
    v = np.zeros(1 << n)
    for s in range(1 << n):
        if s & t == t:
            v[s] = 1.0
    v[0] = 0.0
    return v


def additive_game(values) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    n = len(values)
    v = np.zeros(1 << n)
    for s in range(1 << n):
        v[s] = sum(values[i] for i in range(n) if s >> i & 1)
    return v


def _popcount(x: int) -> int:
    return bin(x).count("1")


def shapley_marginal(v: np.ndarray, n: int) -> np.ndarray:
    sh = np.zeros(n)
    weights = [factorial(k) * factorial(n - k - 1) / factorial(n) for k in range(n)]
    for i in range(n):
        bit = 1 << i
        for s in range(1 << n):
            if s & bit:
                continue
            sh[i] += weights[_popcount(s)] * (v[s | bit] - v[s])
    return sh


def shapley_permutations(v: np.ndarray, n: int) -> np.ndarray:
    sh = np.zeros(n)
    total = 0
    for perm in permutations(range(n)):
        s = 0
        for i in perm:
            sh[i] += v[s | (1 << i)] - v[s]
            s |= 1 << i
        total += 1
    return sh / total


def banzhaf_raw(v: np.ndarray, n: int) -> np.ndarray:
    bz = np.zeros(n)
    for i in range(n):
        bit = 1 << i
        for s in range(1 << n):
            if s & bit:
                continue
            bz[i] += v[s | bit] - v[s]
    return bz / (2 ** (n - 1))


def banzhaf_normalized(v: np.ndarray, n: int) -> np.ndarray:
    raw = banzhaf_raw(v, n)
    return raw / raw.sum()


def weighted_voting_game(weights, quota: float) -> np.ndarray:
    w = np.asarray(weights, dtype=float)
    n = len(w)
    v = np.zeros(1 << n)
    for s in range(1 << n):
        tot = sum(w[i] for i in range(n) if s >> i & 1)
        v[s] = 1.0 if tot >= quota else 0.0
    v[0] = 0.0
    return v


def shapley_shubik(weights, quota: float) -> np.ndarray:
    n = len(weights)
    v = weighted_voting_game(weights, quota)
    return shapley_marginal(v, n)


def is_null_player(v: np.ndarray, n: int, i: int, tol: float = 1e-9) -> bool:
    bit = 1 << i
    for s in range(1 << n):
        if s & bit:
            continue
        if abs(v[s | bit] - v[s]) > tol:
            return False
    return True


def are_symmetric(v: np.ndarray, n: int, i: int, j: int, tol: float = 1e-9) -> bool:
    if i == j:
        return True
    bi, bj = 1 << i, 1 << j
    for s in range(1 << n):
        if s & bi or s & bj:
            continue
        if abs(v[s | bi] - v[s | bj]) > tol:
            return False
    return True
