"""Soluzione di riferimento — Esercizio 01."""
from __future__ import annotations

from collections import namedtuple

import numpy as np

Leaf = namedtuple("Leaf", "value")
Node = namedtuple("Node", "children")

INF = float("inf")


def random_tree(rng: np.random.Generator, depth: int, branching: int,
                lo: int = -20, hi: int = 20):
    if depth == 0:
        return Leaf(int(rng.integers(lo, hi + 1)))
    return Node([random_tree(rng, depth - 1, branching, lo, hi)
                 for _ in range(branching)])


def knuth_moore_bound(branching: int, depth: int) -> int:
    b = branching
    return b ** ((depth + 1) // 2) + b ** (depth // 2) - 1


def count_leaves(node) -> int:
    if isinstance(node, Leaf):
        return 1
    return sum(count_leaves(c) for c in node.children)


def minimax(node, maximizing: bool = True) -> tuple[float, int, int]:
    if isinstance(node, Leaf):
        return float(node.value), 1, 1
    visited, leaves = 1, 0
    best = -INF if maximizing else INF
    for child in node.children:
        val, v, l = minimax(child, not maximizing)
        visited += v
        leaves += l
        best = max(best, val) if maximizing else min(best, val)
    return best, visited, leaves


def alphabeta(node, alpha: float = -INF, beta: float = INF,
              maximizing: bool = True) -> tuple[float, int, int]:
    if isinstance(node, Leaf):
        return float(node.value), 1, 1
    visited, leaves = 1, 0
    if maximizing:
        best = -INF
        for child in node.children:
            val, v, l = alphabeta(child, alpha, beta, False)
            visited += v
            leaves += l
            if val > best:
                best = val
            if best > alpha:
                alpha = best
            if alpha >= beta:          # cut-off: i figli restanti non si visitano
                break
    else:
        best = INF
        for child in node.children:
            val, v, l = alphabeta(child, alpha, beta, True)
            visited += v
            leaves += l
            if val < best:
                best = val
            if best < beta:
                beta = best
            if alpha >= beta:
                break
    return best, visited, leaves


def best_move(node) -> int:
    if isinstance(node, Leaf):
        raise ValueError("best_move non e' definita su una foglia")
    best_idx, best_val = 0, -INF
    for i, child in enumerate(node.children):
        val, _, _ = minimax(child, False)
        if val > best_val:
            best_val, best_idx = val, i
    return best_idx


def order_children(node, maximizing: bool = True):
    if isinstance(node, Leaf):
        return node
    scored = []
    for child in node.children:
        val, _, _ = minimax(child, not maximizing)
        scored.append((val, child))
    scored.sort(key=lambda t: t[0], reverse=maximizing)
    return Node([order_children(c, not maximizing) for _, c in scored])
