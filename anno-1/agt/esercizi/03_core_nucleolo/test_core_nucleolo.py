"""Suite dell'esercizio 03.

Oracolo indipendente: il nucleolo restituito viene confrontato con migliaia di
preimputazioni casuali usando theta calcolato QUI, direttamente dalla definizione,
senza passare dalle funzioni dello studente.
"""
from __future__ import annotations

import importlib.util
import os
from itertools import combinations
from pathlib import Path

import numpy as np
import pytest

_HERE = Path(__file__).parent
_PATH = (_HERE / "soluzione" / "core_nucleolo_sol.py") if os.environ.get("AGT_SOL") == "1" \
    else (_HERE / "core_nucleolo.py")
_spec = importlib.util.spec_from_file_location("mod_under_test_03", _PATH)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

TOL = 1e-6


# --------------------------------------------------------------------------
# Riferimenti indipendenti, scritti nel test e non importati dal modulo.
# --------------------------------------------------------------------------
def _theta_ref(v, n, x):
    """theta(x) ricalcolato dalla definizione, senza usare il codice sotto test."""
    x = np.asarray(x, dtype=float)
    vals = []
    for s in range(1, (1 << n) - 1):
        xs = sum(x[i] for i in range(n) if s >> i & 1)
        vals.append(v[s] - xs)
    return np.sort(np.array(vals))[::-1]


def _lex_leq_ref(a, b, tol=1e-7):
    for u, w in zip(a, b):
        if u < w - tol:
            return True
        if u > w + tol:
            return False
    return True


def _preimputazioni_casuali(rng, v, n, k):
    """k preimputazioni casuali: righe con somma esattamente v(N)."""
    x = rng.normal(0.0, 3.0, size=(k, n))
    x += (v[(1 << n) - 1] - x.sum(axis=1, keepdims=True)) / n
    return x


# --------------------------------------------------------------------------
# Giochi di riferimento.
# --------------------------------------------------------------------------
G_SIMPLESSO = np.array([0.0, 0, 0, 0, 0, 0, 0, 1.0])   # n=3, v(N)=1, tutto il resto 0
G_MAGGIORANZA = np.array([0.0, 0, 0, 1, 0, 1, 1, 1])   # n=3, v(S)=1 se |S|>=2


def test_preimputazione_e_imputazione():
    v = m.additive_game([1.0, 2.0, 3.0])
    assert m.is_preimputation(v, 3, [1, 2, 3])
    assert m.is_preimputation(v, 3, [6, 0, 0])
    assert not m.is_preimputation(v, 3, [1, 1, 1])
    assert m.is_imputation(v, 3, [1, 2, 3])
    assert not m.is_imputation(v, 3, [6, 0, 0])   # viola x_1 >= v({1}) = 2


def test_excess_e_theta():
    v = G_MAGGIORANZA
    x = np.array([0.5, 0.3, 0.2])
    e = m.excess(v, 3, x)
    assert e[0] == pytest.approx(0.0)
    assert e[0b111] == pytest.approx(0.0)
    assert e[0b011] == pytest.approx(1.0 - 0.8)    # coalizione {0,1}
    assert e[0b001] == pytest.approx(0.0 - 0.5)    # coalizione {0}
    th = m.theta(v, 3, x)
    assert th.shape == (2 ** 3 - 2,)
    assert np.allclose(th, _theta_ref(v, 3, x))
    assert np.all(np.diff(th) <= 1e-12)            # ordine decrescente


def test_lex_leq():
    assert m.lex_leq([1, 2, 3], [1, 2, 3])
    assert m.lex_leq([1, 2, 3], [1, 2, 4])
    assert not m.lex_leq([1, 2, 5], [1, 2, 4])
    assert m.lex_leq([0, 9, 9], [1, 0, 0])


def test_in_core_su_esempi_a_mano():
    # gioco del simplesso: il core e' tutto il simplesso unitario
    assert m.in_core(G_SIMPLESSO, 3, [1 / 3, 1 / 3, 1 / 3])
    assert m.in_core(G_SIMPLESSO, 3, [1.0, 0.0, 0.0])
    assert not m.in_core(G_SIMPLESSO, 3, [1.2, -0.2, 0.0])
    # gioco di maggioranza: core vuoto, nessun punto ci sta
    assert not m.in_core(G_MAGGIORANZA, 3, [1 / 3, 1 / 3, 1 / 3])


def test_core_vertices_simplesso():
    vert = m.core_vertices(G_SIMPLESSO, 3)
    assert vert.shape == (3, 3)
    atteso = {(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)}
    ottenuto = {tuple(np.round(r, 6)) for r in vert}
    assert ottenuto == atteso


def test_core_vertices_vuoto_se_core_vuoto():
    assert m.core_vertices(G_MAGGIORANZA, 3).shape[0] == 0


def test_core_vertices_sono_nel_core_e_convessi_ORACOLO():
    """Ogni vertice sta nel core (per definizione) e cosi' ogni loro combinazione."""
    rng = np.random.default_rng(303)
    trovati = 0
    for _ in range(25):
        v = m.random_superadditive_game(rng, 3)
        vert = m.core_vertices(v, 3)
        if vert.shape[0] == 0:
            continue
        trovati += 1
        for r in vert:
            assert m.in_core(v, 3, r, tol=1e-6)
        pesi = rng.dirichlet(np.ones(vert.shape[0]), size=20)
        for w in pesi:
            assert m.in_core(v, 3, w @ vert, tol=1e-6)
    assert trovati >= 5, "test vacuo: nessun gioco con core non vuoto"


def test_least_core_epsilon_segno_coerente_con_core_ORACOLO():
    """eps* <= 0  <=>  core non vuoto. Verificato contro core_vertices."""
    rng = np.random.default_rng(404)
    visti_pos, visti_neg = 0, 0
    pool = [m.random_game(rng, 3) for _ in range(20)]
    pool += [m.random_superadditive_game(rng, 3) for _ in range(20)]
    pool += [G_SIMPLESSO, m.additive_game([1.0, 2.0, 3.0])]
    for v in pool:
        eps = m.least_core_epsilon(v, 3)
        vuoto = m.core_vertices(v, 3).shape[0] == 0
        if vuoto:
            assert eps > 1e-7
            visti_pos += 1
        else:
            assert eps <= 1e-7
            visti_neg += 1
    assert visti_pos > 0 and visti_neg > 0


def test_least_core_epsilon_maggioranza():
    """Gioco di maggioranza a 3: eps* = 1/3, calcolabile a mano."""
    assert m.least_core_epsilon(G_MAGGIORANZA, 3) == pytest.approx(1 / 3, abs=1e-7)


def test_nucleolo_e_una_preimputazione():
    rng = np.random.default_rng(505)
    for _ in range(10):
        v = m.random_game(rng, 3)
        x = m.nucleolus(v, 3)
        assert x.shape == (3,)
        assert x.sum() == pytest.approx(v[-1], abs=1e-6)


def test_nucleolo_casi_a_mano():
    # simmetrico -> divisione equa
    assert np.allclose(m.nucleolus(G_MAGGIORANZA, 3), [1 / 3] * 3, atol=1e-6)
    assert np.allclose(m.nucleolus(G_SIMPLESSO, 3), [1 / 3] * 3, atol=1e-6)
    # additivo -> il vettore dei valori individuali
    v = m.additive_game([1.0, 5.0, -2.0])
    assert np.allclose(m.nucleolus(v, 3), [1.0, 5.0, -2.0], atol=1e-6)


def test_nucleolo_nel_core_quando_il_core_e_non_vuoto():
    rng = np.random.default_rng(606)
    provati = 0
    for _ in range(20):
        v = m.random_superadditive_game(rng, 3)
        if m.core_vertices(v, 3).shape[0] == 0:
            continue
        provati += 1
        assert m.in_core(v, 3, m.nucleolus(v, 3), tol=1e-5)
    assert provati >= 5


def test_nucleolo_lex_minimo_ORACOLO_n3():
    """ORACOLO: theta(nucleolo) <=_lex theta(y) per 4000 preimputazioni casuali.

    theta e' ricalcolato nel test dalla definizione, non chiamando il modulo.
    """
    rng = np.random.default_rng(20260728)
    for _ in range(12):
        v = m.random_game(rng, 3)
        x = m.nucleolus(v, 3)
        th_x = _theta_ref(v, 3, x)
        Y = _preimputazioni_casuali(rng, v, 3, 4000)
        for y in Y:
            assert _lex_leq_ref(th_x, _theta_ref(v, 3, y), tol=1e-7), \
                f"esiste y meglio del nucleolo: v={v}, x={x}, y={y}"


def test_nucleolo_lex_minimo_ORACOLO_n4():
    """Stesso oracolo con n=4 (14 coalizioni proprie), su meno giochi."""
    rng = np.random.default_rng(777)
    for _ in range(4):
        v = m.random_superadditive_game(rng, 4)
        x = m.nucleolus(v, 4)
        th_x = _theta_ref(v, 4, x)
        Y = _preimputazioni_casuali(rng, v, 4, 3000)
        for y in Y:
            assert _lex_leq_ref(th_x, _theta_ref(v, 4, y), tol=1e-7)


def test_nucleolo_batte_anche_i_vertici_del_core_ORACOLO():
    """Confronto con punti non casuali ma strutturati: i vertici del core."""
    rng = np.random.default_rng(888)
    provati = 0
    for _ in range(20):
        v = m.random_superadditive_game(rng, 3)
        vert = m.core_vertices(v, 3)
        if vert.shape[0] == 0:
            continue
        provati += 1
        th_x = _theta_ref(v, 3, m.nucleolus(v, 3))
        for r in vert:
            assert _lex_leq_ref(th_x, _theta_ref(v, 3, r), tol=1e-7)
        for a, b in combinations(range(vert.shape[0]), 2):
            mezzo = 0.5 * (vert[a] + vert[b])
            assert _lex_leq_ref(th_x, _theta_ref(v, 3, mezzo), tol=1e-7)
    assert provati >= 5
