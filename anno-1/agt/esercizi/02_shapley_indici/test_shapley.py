"""Suite dell'esercizio 02.

Oracolo indipendente: la media sulle n! permutazioni, piu' i valori in forma
chiusa dei giochi di unanimita' e additivi, piu' due indici di potere calcolati
a mano su [6; 4, 3, 2].
"""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path

import numpy as np

_HERE = Path(__file__).parent
_PATH = (_HERE / "soluzione" / "shapley_sol.py") if os.environ.get("AGT_SOL") == "1" \
    else (_HERE / "shapley.py")
_spec = importlib.util.spec_from_file_location("mod_under_test_02", _PATH)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

TOL = 1e-9


def test_formula_pesata_uguale_media_permutazioni_ORACOLO():
    """ORACOLO: contributi marginali pesati == media sulle n! permutazioni."""
    for n in (3, 4, 5, 6, 7):
        rng = np.random.default_rng(1000 + n)
        for _ in range(5 if n >= 6 else 20):
            v = m.random_game(rng, n)
            a = m.shapley_marginal(v, n)
            b = m.shapley_permutations(v, n)
            assert np.allclose(a, b, atol=1e-9), f"n={n}: {a} != {b}"


def test_efficienza():
    """sum_i Sh_i(v) = v(N), per costruzione della formula."""
    rng = np.random.default_rng(11)
    for n in (3, 4, 5):
        for _ in range(20):
            v = m.random_game(rng, n)
            assert np.isclose(m.shapley_marginal(v, n).sum(), v[(1 << n) - 1])


def test_gioco_di_unanimita_forma_chiusa():
    """Sh_i(u_T) = 1/|T| per i in T, 0 altrimenti."""
    for n, T in [(3, [0, 1]), (4, [1, 2, 3]), (5, [0]), (5, [0, 1, 2, 3, 4])]:
        v = m.unanimity_game(n, T)
        sh = m.shapley_marginal(v, n)
        atteso = np.array([1.0 / len(T) if i in T else 0.0 for i in range(n)])
        assert np.allclose(sh, atteso, atol=TOL)


def test_gioco_additivo():
    """Su un gioco additivo il valore di Shapley e' il vettore dei valori."""
    vals = [3.0, -1.5, 7.25, 0.0]
    v = m.additive_game(vals)
    assert np.allclose(m.shapley_marginal(v, 4), vals, atol=TOL)


def test_assioma_null_player():
    rng = np.random.default_rng(21)
    n = 4
    for _ in range(15):
        base = m.random_game(rng, n - 1)
        # estende il gioco a n giocatori rendendo l'ultimo un null player
        v = np.zeros(1 << n)
        for s in range(1 << (n - 1)):
            v[s] = base[s]
            v[s | (1 << (n - 1))] = base[s]
        assert m.is_null_player(v, n, n - 1)
        assert np.isclose(m.shapley_marginal(v, n)[n - 1], 0.0, atol=TOL)


def test_assioma_simmetria():
    """Due giocatori simmetrici ricevono lo stesso valore."""
    n = 4
    # gioco che dipende solo dalla cardinalita' della coalizione => tutti simmetrici
    v = np.array([float(bin(s).count("1") ** 2) for s in range(1 << n)])
    v[0] = 0.0
    for i in range(n):
        for j in range(n):
            assert m.are_symmetric(v, n, i, j)
    sh = m.shapley_marginal(v, n)
    assert np.allclose(sh, sh[0], atol=TOL)
    assert np.isclose(sh.sum(), v[-1], atol=TOL)


def test_assioma_additivita():
    """Sh(v + w) = Sh(v) + Sh(w)."""
    rng = np.random.default_rng(31)
    n = 5
    for _ in range(15):
        v = m.random_game(rng, n)
        w = m.random_game(rng, n)
        assert np.allclose(m.shapley_marginal(v + w, n),
                           m.shapley_marginal(v, n) + m.shapley_marginal(w, n),
                           atol=1e-9)


def test_voto_pesato_costruzione():
    v = m.weighted_voting_game([4, 3, 2], 6)
    # A=0(4) B=1(3) C=2(2): vincenti sono AB, AC, ABC
    assert v[m.mask_of([])] == 0
    assert v[m.mask_of([0])] == 0 and v[m.mask_of([1])] == 0 and v[m.mask_of([2])] == 0
    assert v[m.mask_of([0, 1])] == 1
    assert v[m.mask_of([0, 2])] == 1
    assert v[m.mask_of([1, 2])] == 0
    assert v[m.mask_of([0, 1, 2])] == 1


def test_shapley_shubik_a_mano():
    """[6; 4,3,2]: pivot su 6 ordinamenti -> (4/6, 1/6, 1/6). Conto a mano."""
    ss = m.shapley_shubik([4, 3, 2], 6)
    assert np.allclose(ss, [2 / 3, 1 / 6, 1 / 6], atol=TOL)
    assert np.isclose(ss.sum(), 1.0, atol=TOL)


def test_banzhaf_a_mano():
    """[6; 4,3,2]: swing di A=3, B=1, C=1 su 2**2=4 coalizioni."""
    v = m.weighted_voting_game([4, 3, 2], 6)
    raw = m.banzhaf_raw(v, 3)
    assert np.allclose(raw, [3 / 4, 1 / 4, 1 / 4], atol=TOL)
    norm = m.banzhaf_normalized(v, 3)
    assert np.allclose(norm, [3 / 5, 1 / 5, 1 / 5], atol=TOL)


def test_banzhaf_diverso_da_shapley():
    """I due indici NON coincidono: e' il punto della lezione."""
    v = m.weighted_voting_game([4, 3, 2], 6)
    assert not np.allclose(m.banzhaf_normalized(v, 3), m.shapley_shubik([4, 3, 2], 6),
                           atol=1e-6)


def test_banzhaf_non_e_efficiente():
    """In generale sum_i Bz_i(v) != v(N): Banzhaf perde l'efficienza."""
    rng = np.random.default_rng(41)
    n = 4
    trovato = False
    for _ in range(20):
        v = m.random_game(rng, n)
        if not np.isclose(m.banzhaf_raw(v, n).sum(), v[(1 << n) - 1], atol=1e-6):
            trovato = True
            break
    assert trovato


def test_dittatore_e_burattino():
    """[3; 3,1,1]: A e' un dittatore, B e C sono null player."""
    v = m.weighted_voting_game([3, 1, 1], 3)
    assert m.is_null_player(v, 3, 1)
    assert m.is_null_player(v, 3, 2)
    assert m.are_symmetric(v, 3, 1, 2)
    assert np.allclose(m.shapley_shubik([3, 1, 1], 3), [1.0, 0.0, 0.0], atol=TOL)
    assert np.allclose(m.banzhaf_normalized(v, 3), [1.0, 0.0, 0.0], atol=TOL)
