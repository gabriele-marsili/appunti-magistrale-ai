"""Suite dell'esercizio 04.

Oracoli indipendenti: (a) la ricerca esaustiva di TUTTE le coppie bloccanti;
(b) l'enumerazione per forza bruta di TUTTI gli n! matching, da cui si estrae il
proposer-optimal componente per componente e lo si confronta con l'output di
deferred acceptance.
"""
from __future__ import annotations

import importlib.util
import os
from itertools import permutations
from pathlib import Path

import numpy as np

_HERE = Path(__file__).parent
_PATH = (_HERE / "soluzione" / "gale_shapley_sol.py") if os.environ.get("AGT_SOL") == "1" \
    else (_HERE / "gale_shapley.py")
_spec = importlib.util.spec_from_file_location("mod_under_test_04", _PATH)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)


# --- istanza classica a 2, con esattamente due matching stabili -----------
# proponenti: 0 preferisce 0>1 ; 1 preferisce 1>0
# riceventi : 0 preferisce 1>0 ; 1 preferisce 0>1
DUE_P = np.array([[0, 1], [1, 0]])
DUE_R = np.array([[1, 0], [0, 1]])


def _stabile_ref(mu, prop_prefs, recv_prefs):
    """Stabilita' ricalcolata nel test, senza usare il codice sotto esame."""
    mu = np.asarray(mu)
    n = len(mu)
    inv = {int(mu[p]): p for p in range(n)}
    pp = [list(r) for r in np.asarray(prop_prefs)]
    rr = [list(r) for r in np.asarray(recv_prefs)]
    for p in range(n):
        for r in range(n):
            if mu[p] == r:
                continue
            if pp[p].index(r) < pp[p].index(int(mu[p])) and \
               rr[r].index(p) < rr[r].index(inv[r]):
                return False
    return True


def test_rank_matrix():
    prefs = np.array([[2, 0, 1], [0, 1, 2]])
    R = m.rank_matrix(prefs)
    assert R.tolist() == [[1, 2, 0], [0, 1, 2]]


def test_da_e_una_biiezione():
    rng = np.random.default_rng(1)
    for n in (2, 3, 4, 5, 6):
        for _ in range(20):
            pp, rr = m.random_instance(rng, n)
            mu, _ = m.deferred_acceptance(pp, rr)
            assert sorted(mu.tolist()) == list(range(n))


def test_da_termina_entro_n_quadro():
    rng = np.random.default_rng(2)
    for n in (3, 5, 7):
        for _ in range(20):
            pp, rr = m.random_instance(rng, n)
            _, n_prop = m.deferred_acceptance(pp, rr)
            assert n_prop <= n * n


def test_blocking_pairs_su_esempio_a_mano():
    # matching "sbagliato" sull'istanza a 2: 0->1, 1->0
    mu = np.array([1, 0])
    bp = m.blocking_pairs(mu, DUE_P, DUE_R)
    # 0 preferisce il ricevente 0 (ha 1) e il ricevente 0 preferisce 1 (ha 1)?
    # rank_r[0] = [1,0] quindi il ricevente 0 preferisce 1, che gia' ha -> no.
    # 1 preferisce il ricevente 1 (ha 0) e il ricevente 1 preferisce 0, che ha -> no.
    assert bp == []
    assert m.is_stable(mu, DUE_P, DUE_R)


def test_da_produce_un_matching_stabile_ORACOLO():
    """ORACOLO: nessuna coppia bloccante, cercata su tutte le n**2 coppie."""
    rng = np.random.default_rng(20260728)
    for n in (2, 3, 4, 5, 6):
        for _ in range(40):
            pp, rr = m.random_instance(rng, n)
            mu, _ = m.deferred_acceptance(pp, rr)
            assert _stabile_ref(mu, pp, rr), f"DA ha prodotto un matching instabile: {mu}"
            assert m.blocking_pairs(mu, pp, rr) == []


def test_all_stable_matchings_su_istanza_a_due():
    stabili = m.all_stable_matchings(DUE_P, DUE_R)
    trovati = {tuple(mu.tolist()) for mu in stabili}
    assert trovati == {(0, 1), (1, 0)}


def test_all_stable_matchings_coerente_con_forza_bruta_ORACOLO():
    rng = np.random.default_rng(4)
    for n in (2, 3, 4, 5):
        for _ in range(15):
            pp, rr = m.random_instance(rng, n)
            atteso = {perm for perm in permutations(range(n))
                      if _stabile_ref(np.array(perm), pp, rr)}
            ottenuto = {tuple(mu.tolist()) for mu in m.all_stable_matchings(pp, rr)}
            assert ottenuto == atteso


def test_esiste_sempre_almeno_un_matching_stabile():
    rng = np.random.default_rng(5)
    for n in (2, 3, 4, 5):
        for _ in range(20):
            pp, rr = m.random_instance(rng, n)
            assert len(m.all_stable_matchings(pp, rr)) >= 1


def test_da_e_proposer_optimal_ORACOLO():
    """ORACOLO: l'output di DA coincide con il best-stable-partner di ciascun
    proponente, costruito componente per componente su TUTTI i matching stabili."""
    rng = np.random.default_rng(6)
    con_piu_di_uno = 0
    for n in (2, 3, 4, 5):
        for _ in range(25):
            pp, rr = m.random_instance(rng, n)
            stabili = m.all_stable_matchings(pp, rr)
            if len(stabili) > 1:
                con_piu_di_uno += 1
            best = m.best_stable_partner(stabili, pp)
            mu, _ = m.deferred_acceptance(pp, rr)
            assert np.array_equal(mu, best), f"DA {mu} != proposer-optimal {best}"
    assert con_piu_di_uno >= 10, "test quasi vacuo: quasi nessuna istanza multi-stabile"


def test_best_stable_partner_e_esso_stesso_stabile():
    """Il teorema del reticolo: il vettore dei migliori partner stabili e' un matching."""
    rng = np.random.default_rng(7)
    for n in (2, 3, 4, 5):
        for _ in range(25):
            pp, rr = m.random_instance(rng, n)
            stabili = m.all_stable_matchings(pp, rr)
            best = m.best_stable_partner(stabili, pp)
            assert sorted(best.tolist()) == list(range(n))
            assert _stabile_ref(best, pp, rr)


def test_da_dal_lato_ricevente_e_proposer_pessimal_per_i_proponenti():
    """Scambiando i ruoli si ottiene il matching PEGGIORE per i proponenti."""
    rng = np.random.default_rng(8)
    for n in (2, 3, 4, 5):
        for _ in range(25):
            pp, rr = m.random_instance(rng, n)
            mu_r, _ = m.deferred_acceptance(rr, pp)     # riceventi che propongono
            mu = m.inverti(mu_r)                        # riportato sul lato proponenti
            stabili = m.all_stable_matchings(pp, rr)
            worst = m.worst_stable_partner(stabili, pp)
            assert np.array_equal(mu, worst)


def test_ordine_dei_liberi_non_cambia_il_risultato():
    """DA e' indipendente dall'ordine in cui si servono i proponenti liberi."""
    rng = np.random.default_rng(9)
    for _ in range(30):
        pp, rr = m.random_instance(rng, 5)
        mu1, _ = m.deferred_acceptance(pp, rr)
        perm = rng.permutation(5)
        inv = np.argsort(perm)
        pp2 = pp[perm]
        rr2 = np.array([[inv[x] for x in riga] for riga in rr])
        mu2, _ = m.deferred_acceptance(pp2, rr2)
        assert np.array_equal(mu2, mu1[perm])
