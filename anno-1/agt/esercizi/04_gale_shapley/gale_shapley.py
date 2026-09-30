"""
Esercizio 04 — Matching two-sided, Gale-Shapley e stabilita' (L18).

Convenzioni.
  - Due lati di uguale cardinalita' n: PROPONENTI 0..n-1 e RICEVENTI 0..n-1.
  - `prop_prefs` e' un array (n, n) di interi: `prop_prefs[p]` e' la lista
    ordinata dei riceventi, dal piu' gradito al meno gradito.
  - `recv_prefs` e' un array (n, n): `recv_prefs[r]` e' la lista ordinata dei
    proponenti. Preferenze STRETTE, nessuna indifferenza, nessun partner
    inaccettabile (come nel problema del matrimonio delle slide).
  - Un matching e' un array `mu` di lunghezza n con `mu[p] = r`: e' una biiezione
    fra i due lati.

Le funzioni con "# TODO" sono da implementare.
"""
from __future__ import annotations

from itertools import permutations

import numpy as np


# --------------------------------------------------------------------------
# Codice fornito.
# --------------------------------------------------------------------------
def random_instance(rng: np.random.Generator, n: int):
    """Istanza casuale: due matrici (n, n) di preferenze strette. Deterministica."""
    prop = np.array([rng.permutation(n) for _ in range(n)])
    recv = np.array([rng.permutation(n) for _ in range(n)])
    return prop, recv


def inverti(mu: np.ndarray) -> np.ndarray:
    """Matching visto dall'altro lato: `inv[r] = p` se `mu[p] = r`."""
    inv = np.empty_like(mu)
    inv[mu] = np.arange(len(mu))
    return inv


# --------------------------------------------------------------------------
# Da implementare.
# --------------------------------------------------------------------------
def rank_matrix(prefs: np.ndarray) -> np.ndarray:
    """Matrice dei ranghi: `R[i, j]` = posizione di j nella lista di i (0 = migliore).

    Serve a confrontare due partner in tempo costante invece che cercandoli
    nella lista. Esempio: `prefs[0] = [2, 0, 1]` -> `R[0] = [1, 2, 0]`.
    """
    raise NotImplementedError("TODO: rank_matrix")  # TODO


def deferred_acceptance(prop_prefs: np.ndarray, recv_prefs: np.ndarray):
    """Algoritmo di Gale-Shapley (1962) con i proponenti che propongono.

    Ritorna ``(mu, n_proposte)`` dove `mu[p]` e' il ricevente assegnato a p e
    `n_proposte` e' il numero totale di proposte fatte.

    Schema: finche' esiste un proponente libero, propone al ricevente piu'
    gradito a cui non ha ancora proposto; il ricevente tiene provvisoriamente il
    migliore fra il pretendente attuale e quello che aveva ("deferred"), e
    rifiuta l'altro. Nessun rifiuto e' definitivo finche' l'algoritmo non termina.

    Il numero di proposte non puo' superare n**2: ogni proponente propone a ogni
    ricevente al piu' una volta.
    """
    raise NotImplementedError("TODO: deferred_acceptance")  # TODO


def blocking_pairs(mu: np.ndarray, prop_prefs: np.ndarray,
                   recv_prefs: np.ndarray) -> list[tuple[int, int]]:
    """TUTTE le coppie bloccanti di `mu`, cercate esaustivamente.

    (p, r) blocca `mu` se p preferisce r al proprio partner `mu[p]` E r preferisce
    p al proprio partner corrente. Va scandita ogni coppia (p, r), senza scorciatoie:
    e' questa la verifica indipendente della stabilita'.

    Ritorna la lista ordinata delle coppie.
    """
    raise NotImplementedError("TODO: blocking_pairs")  # TODO


def is_stable(mu: np.ndarray, prop_prefs: np.ndarray,
              recv_prefs: np.ndarray) -> bool:
    """Un matching e' stabile se non ha nessuna coppia bloccante."""
    raise NotImplementedError("TODO: is_stable")  # TODO


def all_stable_matchings(prop_prefs: np.ndarray,
                         recv_prefs: np.ndarray) -> list[np.ndarray]:
    """TUTTI i matching stabili, per forza bruta sulle n! biiezioni.

    Praticabile fino a n = 6 (720 permutazioni). Ritorna la lista dei matching
    stabili, ciascuno come array di lunghezza n.
    """
    raise NotImplementedError("TODO: all_stable_matchings")  # TODO


def best_stable_partner(stabili: list[np.ndarray], prop_prefs: np.ndarray) -> np.ndarray:
    """Per ogni proponente, il partner migliore fra tutti i matching stabili.

    Il teorema di Gale-Shapley dice che questo vettore E' ESSO STESSO un matching
    stabile (il proposer-optimal), ma qui va costruito componente per componente,
    senza assumerlo: e' proprio quello che il test deve verificare.
    """
    raise NotImplementedError("TODO: best_stable_partner")  # TODO


def worst_stable_partner(stabili: list[np.ndarray], prop_prefs: np.ndarray) -> np.ndarray:
    """Per ogni proponente, il partner peggiore fra tutti i matching stabili."""
    raise NotImplementedError("TODO: worst_stable_partner")  # TODO
