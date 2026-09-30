"""Suite dell'esercizio 01. Oracolo indipendente: il minimax NON potato."""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path

import numpy as np
import pytest

_HERE = Path(__file__).parent
_PATH = (_HERE / "soluzione" / "alfabeta_sol.py") if os.environ.get("AGT_SOL") == "1" \
    else (_HERE / "alfabeta.py")
_spec = importlib.util.spec_from_file_location("mod_under_test_01", _PATH)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

Leaf, Node = m.Leaf, m.Node


# --- albero di riferimento calcolato a mano ------------------------------
# MAX
#  |- MIN [3, 12, 8]      -> 3
#  |- MIN [2, 4, 6]       -> 2
#  |- MIN [14, 5, 2]      -> 2
# valore alla radice = 3, mossa migliore = 0
HAND = Node([
    Node([Leaf(3), Leaf(12), Leaf(8)]),
    Node([Leaf(2), Leaf(4), Leaf(6)]),
    Node([Leaf(14), Leaf(5), Leaf(2)]),
])


def test_count_leaves_albero_uniforme():
    rng = np.random.default_rng(0)
    for depth, b in [(1, 2), (2, 3), (3, 2), (4, 2)]:
        t = m.random_tree(rng, depth, b)
        assert m.count_leaves(t) == b ** depth


def test_valore_a_mano():
    assert m.minimax(HAND)[0] == 3.0
    assert m.alphabeta(HAND)[0] == 3.0
    assert m.best_move(HAND) == 0


def test_best_move_su_foglia_solleva():
    with pytest.raises(ValueError):
        m.best_move(Leaf(7))


def test_alfabeta_coincide_con_minimax_ORACOLO():
    """ORACOLO: su 300 alberi casuali il valore potato == valore non potato."""
    rng = np.random.default_rng(20260728)
    for _ in range(300):
        depth = int(rng.integers(1, 5))
        b = int(rng.integers(2, 4))
        t = m.random_tree(rng, depth, b)
        v_full, _, _ = m.minimax(t)
        v_ab, _, _ = m.alphabeta(t)
        assert v_ab == v_full, f"potatura ha cambiato il valore: {v_ab} != {v_full}"


def test_minimax_visita_tutto():
    rng = np.random.default_rng(7)
    for depth, b in [(2, 3), (3, 2), (4, 2)]:
        t = m.random_tree(rng, depth, b)
        n_nodi = sum(b ** k for k in range(depth + 1))
        _, visited, leaves = m.minimax(t)
        assert visited == n_nodi
        assert leaves == b ** depth


def test_alfabeta_non_visita_mai_piu_del_minimax():
    rng = np.random.default_rng(1234)
    for _ in range(200):
        t = m.random_tree(rng, 4, 3)
        _, v_full, l_full = m.minimax(t)
        _, v_ab, l_ab = m.alphabeta(t)
        assert v_ab <= v_full
        assert l_ab <= l_full


def test_alfabeta_risparmia_davvero():
    """Il risparmio medio sulle foglie deve essere sostanziale (>25%)."""
    rng = np.random.default_rng(99)
    ratios = []
    for _ in range(200):
        t = m.random_tree(rng, 4, 3)
        _, _, l_full = m.minimax(t)
        _, _, l_ab = m.alphabeta(t)
        ratios.append(l_ab / l_full)
    assert float(np.mean(ratios)) < 0.75


def test_bound_di_knuth_moore_e_rispettato():
    """Nessun ordinamento puo' scendere sotto b**ceil(d/2)+b**floor(d/2)-1."""
    rng = np.random.default_rng(5)
    for b, depth in [(2, 4), (3, 3), (2, 6)]:
        bound = m.knuth_moore_bound(b, depth)
        for _ in range(50):
            t = m.random_tree(rng, depth, b)
            _, _, l_ab = m.alphabeta(t)
            assert l_ab >= bound


def test_ordinamento_best_first_conserva_il_valore_e_riduce_le_foglie():
    rng = np.random.default_rng(4242)
    gains = []
    for _ in range(60):
        t = m.random_tree(rng, 4, 3)
        t_ord = m.order_children(t)
        v0, _, l0 = m.alphabeta(t)
        v1, _, l1 = m.alphabeta(t_ord)
        assert v1 == v0, "riordinare i figli non deve cambiare il valore minimax"
        assert l1 <= l0
        gains.append(l1 / l0)
    assert float(np.mean(gains)) < 0.9


def test_ordinamento_best_first_si_avvicina_al_bound():
    """Con l'ordinamento perfetto l'alfa-beta deve stare vicino a Knuth-Moore."""
    rng = np.random.default_rng(2026)
    b, depth = 3, 4
    bound = m.knuth_moore_bound(b, depth)
    for _ in range(40):
        t = m.order_children(m.random_tree(rng, depth, b))
        _, _, l_ab = m.alphabeta(t)
        assert bound <= l_ab <= 2 * bound
