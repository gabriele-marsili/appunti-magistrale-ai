"""
Esercizio 01 — Minimax sequenziale e alfa-beta pruning (L12).

Rappresentazione dell'albero di enumerazione (slide L11): un nodo e' o una
foglia con un payoff, o un nodo interno con una lista di figli. La radice e'
di MAX (giocatore I); i livelli si alternano MAX/MIN.

Le funzioni con "# TODO" sono da implementare.
"""
from __future__ import annotations

from collections import namedtuple

import numpy as np

Leaf = namedtuple("Leaf", "value")
Node = namedtuple("Node", "children")

INF = float("inf")


# --------------------------------------------------------------------------
# Codice fornito: generatore deterministico di alberi.
# --------------------------------------------------------------------------
def random_tree(rng: np.random.Generator, depth: int, branching: int,
                lo: int = -20, hi: int = 20):
    """Albero uniforme di profondita' `depth` e fattore di ramificazione `branching`.

    Le foglie hanno payoff interi in [lo, hi]. Deterministico dato `rng`.
    """
    if depth == 0:
        return Leaf(int(rng.integers(lo, hi + 1)))
    return Node([random_tree(rng, depth - 1, branching, lo, hi)
                 for _ in range(branching)])


def knuth_moore_bound(branching: int, depth: int) -> int:
    """Numero minimo di FOGLIE che l'alfa-beta deve valutare (Knuth-Moore 1975).

    b**ceil(d/2) + b**floor(d/2) - 1. E' il caso migliore, raggiunto solo con
    l'ordinamento perfetto dei figli.
    """
    b = branching
    return b ** ((depth + 1) // 2) + b ** (depth // 2) - 1


# --------------------------------------------------------------------------
# Da implementare.
# --------------------------------------------------------------------------
def count_leaves(node) -> int:
    """Numero di foglie del sottoalbero radicato in `node`."""
    raise NotImplementedError("TODO: count_leaves")  # TODO


def minimax(node, maximizing: bool = True) -> tuple[float, int, int]:
    """Minimax NON potato.

    Ritorna la tripla ``(valore, nodi_visitati, foglie_valutate)``:
      - `valore`: valore minimax del nodo, con MAX al livello corrente se
        `maximizing` e' True;
      - `nodi_visitati`: quanti nodi (interni + foglie) sono stati attraversati,
        contando anche `node` stesso;
      - `foglie_valutate`: quante foglie sono state lette.

    Senza potatura questi due contatori coprono tutto l'albero.
    """
    raise NotImplementedError("TODO: minimax")  # TODO


def alphabeta(node, alpha: float = -INF, beta: float = INF,
              maximizing: bool = True) -> tuple[float, int, int]:
    """Minimax con potatura alfa-beta.

    Stessa tripla di ritorno di `minimax`. Il valore DEVE coincidere con quello
    di `minimax` sullo stesso albero: la potatura taglia rami che non possono
    cambiare il risultato, non cambia il risultato.

    Invariante da rispettare: appena il valore corrente esce dalla finestra
    [alpha, beta] si interrompe la scansione dei figli rimanenti (cut-off), e
    quei figli NON vanno contati fra i nodi visitati.
    """
    raise NotImplementedError("TODO: alphabeta")  # TODO


def best_move(node) -> int:
    """Indice del figlio della radice che realizza il valore minimax.

    La radice e' di MAX. A parita' di valore, ritorna l'indice piu' piccolo.
    Su una foglia solleva `ValueError`.
    """
    raise NotImplementedError("TODO: best_move")  # TODO


def order_children(node, maximizing: bool = True):
    """Riordina ricorsivamente i figli di ogni nodo interno in modo "best-first".

    In un nodo di MAX i figli vanno ordinati per valore minimax DECRESCENTE,
    in un nodo di MIN per valore CRESCENTE. E' l'ordinamento che rende
    l'alfa-beta massimamente efficace: su un albero cosi' ordinato il numero di
    foglie valutate deve avvicinarsi al bound di Knuth-Moore.

    Ritorna un NUOVO albero, non modifica quello in ingresso.
    """
    raise NotImplementedError("TODO: order_children")  # TODO
