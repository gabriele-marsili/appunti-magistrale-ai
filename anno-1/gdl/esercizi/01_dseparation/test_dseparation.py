"""Suite di autovalutazione per l'esercizio sulla d-separazione.

    pytest test_dseparation.py -v            # testa lo skeleton (deve fallire)
    GDL_SOL=1 pytest test_dseparation.py -v  # testa la soluzione (deve passare)
"""

import os, sys, pathlib, importlib

HERE = pathlib.Path(__file__).parent
if os.environ.get("GDL_SOL"):
    sys.path.insert(0, str(HERE / "soluzione"))
    m = importlib.import_module("dseparation_sol")
else:
    sys.path.insert(0, str(HERE))
    m = importlib.import_module("dseparation")

import itertools
import re
from collections import defaultdict

import numpy as np
import pytest

# DAG degeneri usati nei casi limite
SINGLE = {"A": []}
DISCONNECTED = {"A": [], "B": []}


# ----------------------------------------------------------------------
# Oracoli e utilita' del test — NON usano il codice dello studente.
# ----------------------------------------------------------------------

def _ci_deviation(joint, order, X, Y, Z):
    """Massima violazione di  P(x,y,z) P(z) = P(x,z) P(y,z).

    E' la definizione di indipendenza condizionale scritta in forma prodotto
    (niente divisioni, quindi nessun problema con P(z) = 0).  Calcolata per
    forza bruta enumerando ogni cella della tabella congiunta.  Zero (a meno
    dell'errore macchina) <=> X e' indipendente da Y dato Z.
    """
    pos = {n: i for i, n in enumerate(order)}
    pxyz, pxz, pyz, pz = (defaultdict(float) for _ in range(4))
    for cell in itertools.product(*[range(s) for s in joint.shape]):
        p = float(joint[cell])
        kx = tuple(cell[pos[n]] for n in X)
        ky = tuple(cell[pos[n]] for n in Y)
        kz = tuple(cell[pos[n]] for n in Z)
        pxyz[(kx, ky, kz)] += p
        pxz[(kx, kz)] += p
        pyz[(ky, kz)] += p
        pz[kz] += p
    return max(
        abs(v * pz[kz] - pxz[(kx, kz)] * pyz[(ky, kz)])
        for (kx, ky, kz), v in pxyz.items()
    )


def _subsets(items):
    for k in range(len(items) + 1):
        for c in itertools.combinations(items, k):
            yield list(c)


# ----------------------------------------------------------------------
# 1-3: accessori sul grafo
# ----------------------------------------------------------------------

def test_parents_e_children():
    """parents legge dag[node], children va ricavato scandendo il grafo."""
    assert m.parents(m.STUDENT, "G") == ["D", "I"], \
        "parents(G) deve restituire dag['G'] nell'ordine memorizzato ['D','I']"
    assert m.parents(m.STUDENT, "D") == [], \
        "un nodo radice ha lista di genitori vuota, non None"
    assert m.children(m.STUDENT, "I") == ["G", "S"], \
        "children(I) = nodi che hanno I fra i genitori, in ordine alfabetico"
    assert m.children(m.STUDENT, "L") == [], \
        "una foglia non ha figli"
    assert m.children(m.STUDENT, "D") == ["G"], \
        "children non deve confondere genitori e figli: D ha solo il figlio G"

    fuori = m.parents(m.STUDENT, "G")
    fuori.append("HACK")
    assert m.STUDENT["G"] == ["D", "I"], \
        "parents deve restituire una COPIA: il DAG non va corrotto dal chiamante"


def test_ancestors():
    """La chiusura ancestrale include i nodi di partenza."""
    assert m.ancestors(m.STUDENT, ["L"]) == {"L", "G", "D", "I"}, \
        "An({L}) deve risalire tutta la catena e contenere L stesso"
    assert m.ancestors(m.STUDENT, ["S"]) == {"S", "I"}, \
        "An({S}) non deve includere D e G: non sono antenati di S"
    assert m.ancestors(m.STUDENT, []) == set(), \
        "An(insieme vuoto) e' l'insieme vuoto"
    assert m.ancestors(m.STUDENT, ["D", "S"]) == {"D", "S", "I"}, \
        "An deve essere la chiusura sull'UNIONE dei nodi dati"
    assert m.ancestors(m.COLLIDER, ["W"]) == {"W", "Z", "X", "Y"}, \
        "An({W}) risale il collider fino a entrambi i genitori X e Y"


def test_markov_blanket():
    """Il blanket contiene anche i CO-GENITORI dei figli, non solo pa/ch."""
    assert m.markov_blanket(m.STUDENT, "D") == {"G", "I"}, \
        "Mb(D): il figlio G piu' il co-genitore I; dimenticare I e' l'errore tipico"
    assert m.markov_blanket(m.STUDENT, "I") == {"G", "S", "D"}, \
        "Mb(I): figli G,S piu' il co-genitore D di G"
    assert m.markov_blanket(m.STUDENT, "G") == {"D", "I", "L"}, \
        "Mb(G): genitori D,I e figlio L"
    assert m.markov_blanket(m.STUDENT, "L") == {"G"}, \
        "Mb(L): solo il genitore G"
    assert "G" not in m.markov_blanket(m.STUDENT, "G"), \
        "il blanket di un nodo non contiene il nodo stesso"
    assert m.markov_blanket(SINGLE, "A") == set(), \
        "un nodo isolato ha blanket vuoto"


def test_markov_blanket_scherma_ed_e_minimale():
    """Proprieta': Mb(v) d-separa v dal resto, e nessun sottoinsieme lo fa."""
    for dag in (m.CHAIN, m.COLLIDER, m.STUDENT):
        for v in dag:
            mb = m.markov_blanket(dag, v)
            resto = set(dag) - {v} - mb
            assert m.is_dseparated(dag, [v], resto, mb), \
                f"Mb({v}) deve d-separare {v} da tutto il resto della rete"
            for togli in sorted(mb):
                mb2 = mb - {togli}
                resto2 = set(dag) - {v} - mb2
                assert not m.is_dseparated(dag, [v], resto2, mb2), \
                    (f"Mb({v}) deve essere MINIMALE: togliendo {togli} la "
                     f"schermatura deve rompersi")


# ----------------------------------------------------------------------
# 5-6: fattorizzazione
# ----------------------------------------------------------------------

def test_factorization():
    """Un fattore P(v|pa(v)) per nodo, in ordine topologico."""
    assert m.factorization(m.CHAIN) == "P(A)P(B|A)P(C|B)", \
        "catena A->B->C: P(A)P(B|A)P(C|B)"
    assert m.factorization(m.COLLIDER) == "P(X)P(Y)P(Z|X,Y)P(W|Z)", \
        "collider: i due genitori X,Y sono marginali, Z condiziona su entrambi"
    assert m.factorization(m.STUDENT) == "P(D)P(I)P(G|D,I)P(L|G)P(S|I)", \
        "rete Student: ordine topologico D,I,G,L,S e genitori separati da virgola"
    assert m.factorization(SINGLE) == "P(A)", \
        "un solo nodo senza genitori: P(A)"
    assert m.factorization(DISCONNECTED) == "P(A)P(B)", \
        "due nodi indipendenti: nessuna barra verticale"


def test_factorization_ricostruisce_la_congiunta():
    """Oracolo: la stringa, letta come ricetta, deve ridare la congiunta esatta."""
    dag, cards = m.STUDENT, m.STUDENT_CARDS
    cpts = m.random_cpts(dag, cards, seed=3)
    joint, order = m.enumerate_joint(dag, cards, cpts=cpts)

    testo = m.factorization(dag)
    fattori = re.findall(r"P\(([A-Za-z0-9_]+)(?:\|([^)]*))?\)", testo)
    assert len(fattori) == len(dag), \
        f"la fattorizzazione deve avere un fattore per nodo, trovati {len(fattori)}"

    visti = []
    ricetta = []
    for nodo, pa_str in fattori:
        pa = [p for p in pa_str.split(",") if p] if pa_str else []
        assert set(pa) == set(dag[nodo]), \
            f"il fattore di {nodo} deve condizionare esattamente su pa({nodo})"
        assert all(p in visti for p in pa), \
            f"ordine non topologico: i genitori di {nodo} compaiono dopo {nodo}"
        visti.append(nodo)
        ricetta.append((nodo, pa))

    # ricostruzione a mano, cella per cella, senza numpy broadcasting
    pos = {n: i for i, n in enumerate(order)}
    tot = 0.0
    for cell in itertools.product(*[range(cards[n]) for n in order]):
        p = 1.0
        for nodo, pa in ricetta:
            idx = tuple(cell[pos[q]] for q in pa) + (cell[pos[nodo]],)
            p *= float(cpts[nodo][idx])
        assert abs(p - float(joint[cell])) < 1e-12, \
            f"la fattorizzazione non riproduce la congiunta nella cella {cell}"
        tot += p
    assert abs(tot - 1.0) < 1e-9, \
        "la congiunta ricostruita dalla fattorizzazione deve normalizzare a 1"


# ----------------------------------------------------------------------
# 7-10: d-separazione
# ----------------------------------------------------------------------

def test_dsep_catena():
    """Head-to-tail: osservare il nodo di mezzo BLOCCA il cammino."""
    assert not m.is_dseparated(m.CHAIN, ["A"], ["C"], []), \
        "A->B->C: senza osservare B, A e C sono marginalmente dipendenti"
    assert m.is_dseparated(m.CHAIN, ["A"], ["C"], ["B"]), \
        "A->B->C: osservando B la catena e' bloccata, A indipendente da C dato B"
    assert not m.is_dseparated(m.CHAIN, ["A"], ["B"], ["C"]), \
        "nodi adiacenti non sono mai d-separati, qualunque sia Z"


def test_dsep_collider():
    """Head-to-head: il collider si comporta AL CONTRARIO di catena e fork."""
    assert m.is_dseparated(m.COLLIDER, ["X"], ["Y"], []), \
        "X->Z<-Y: con Z non osservato il collider blocca, X e Y sono indipendenti"
    assert not m.is_dseparated(m.COLLIDER, ["X"], ["Y"], ["Z"]), \
        "osservare il collider Z SBLOCCA il cammino (explaining away)"
    assert not m.is_dseparated(m.COLLIDER, ["X"], ["Y"], ["W"]), \
        "anche osservare un DISCENDENTE W del collider sblocca il cammino"
    assert not m.is_dseparated(m.COLLIDER, ["X"], ["Y"], ["Z", "W"]), \
        "osservare collider e discendente insieme lascia il cammino attivo"
    assert m.is_dseparated(m.COLLIDER, ["X"], ["W"], ["Z"]), \
        "X->Z->W e' una catena: osservare Z la blocca"


def test_dsep_student():
    """Le (in)dipendenze note della rete Student di Koller."""
    S = m.STUDENT
    assert m.is_dseparated(S, ["D"], ["I"], []), \
        "D e I sono marginalmente indipendenti: G e' un collider non osservato"
    assert not m.is_dseparated(S, ["D"], ["I"], ["G"]), \
        "osservando il voto G, difficolta' e intelligenza diventano dipendenti"
    assert not m.is_dseparated(S, ["D"], ["I"], ["L"]), \
        "L e' discendente del collider G: osservarlo rende D e I dipendenti"
    assert m.is_dseparated(S, ["D"], ["S"], []), \
        "D e S sono separati: il solo cammino passa dal collider G non osservato"
    assert not m.is_dseparated(S, ["D"], ["S"], ["G"]), \
        "aprendo il collider G il cammino D-G-I-S diventa attivo"
    assert m.is_dseparated(S, ["D"], ["S"], ["G", "I"]), \
        "osservando anche I il fork G<-I->S si richiude: D indipendente da S"
    assert m.is_dseparated(S, ["L"], ["S"], ["G", "I"]), \
        "con G e I osservati L e S sono separati"
    assert m.is_dseparated(S, ["L"], ["D", "I", "S"], ["G"]), \
        "G e' il blanket di L: lo separa da tutto il resto"


def test_dsep_simmetria():
    """Proprieta': la d-separazione e' simmetrica in X e Y."""
    for dag in (m.CHAIN, m.COLLIDER, m.STUDENT):
        nodi = sorted(dag)
        for x, y in itertools.combinations(nodi, 2):
            resto = [n for n in nodi if n not in (x, y)]
            for Z in _subsets(resto):
                a = m.is_dseparated(dag, [x], [y], Z)
                b = m.is_dseparated(dag, [y], [x], Z)
                assert a == b, \
                    f"d-separazione non simmetrica per {x},{y} dato {Z}"
                if x in dag[y] or y in dag[x]:
                    assert not a, \
                        (f"{x} e {y} sono adiacenti: nessun Z puo' separarli, "
                         f"ma con Z={Z} il risultato e' True")


def test_active_paths():
    """I cammini attivi devono spiegare esattamente le non-separazioni."""
    # contenuto esplicito
    assert m.active_paths(m.COLLIDER, "X", "Y", []) == [], \
        "senza condizionamento il collider blocca: nessun cammino attivo"
    assert [tuple(p) for p in m.active_paths(m.COLLIDER, "X", "Y", ["W"])] == \
        [("X", "Z", "Y")], \
        "condizionando sul discendente W il cammino X-Z-Y torna attivo"
    assert [tuple(p) for p in m.active_paths(m.STUDENT, "D", "S", ["G"])] == \
        [("D", "G", "I", "S")], \
        "condizionando su G l'unico cammino attivo fra D e S e' D-G-I-S"
    assert m.active_paths(m.STUDENT, "D", "S", ["G", "I"]) == [], \
        "osservando anche I il cammino si richiude sul fork centrato in I"

    # equivalenza con is_dseparated: due algoritmi diversi, stesso verdetto
    for dag in (m.CHAIN, m.COLLIDER, m.STUDENT):
        nodi = sorted(dag)
        for x, y in itertools.combinations(nodi, 2):
            resto = [n for n in nodi if n not in (x, y)]
            for Z in _subsets(resto):
                sep = m.is_dseparated(dag, [x], [y], Z)
                cam = m.active_paths(dag, x, y, Z)
                assert sep == (len(cam) == 0), \
                    (f"{x},{y} dato {Z}: is_dseparated={sep} ma active_paths "
                     f"ha trovato {cam}")
                for p in cam:
                    assert p[0] == x and p[-1] == y, \
                        "ogni cammino deve partire da x e finire in y"
                    assert len(set(p)) == len(p), \
                        "i cammini devono essere semplici, senza nodi ripetuti"


# ----------------------------------------------------------------------
# 12: oracolo numerico indipendente
# ----------------------------------------------------------------------

def test_oracolo_numerico_dsep_implica_indipendenza():
    """Oracolo: la d-separazione grafica va confrontata con la congiunta vera.

    Si costruisce numericamente la distribuzione congiunta da CPT casuali (seed
    fissato) e si verifica per marginalizzazione se X e Y sono davvero
    indipendenti dato Z.  Nessuna nozione di grafo entra in questo calcolo.

    Direzione 1 (Global Markov property, sempre vera): d-separazione =>
    indipendenza numerica.
    Direzione 2 (faithfulness, vera quasi ovunque per CPT casuali):
    non d-separazione => dipendenza numericamente rilevabile.
    """
    IND, DIP = 1e-12, 1e-6   # soglie: con questo seed lo stacco reale e' 1e-16 vs 9e-5

    # --- caso collider, esplicito ---
    jc, oc = m.enumerate_joint(m.COLLIDER, m.COLLIDER_CARDS, seed=7)
    np.testing.assert_allclose(jc.sum(), 1.0, rtol=1e-6, atol=1e-9)

    assert m.is_dseparated(m.COLLIDER, ["X"], ["Y"], []) and \
        _ci_deviation(jc, oc, ["X"], ["Y"], []) < IND, \
        "X->Z<-Y: dato l'insieme vuoto X e Y devono essere sia d-separati sia " \
        "numericamente indipendenti"
    assert not m.is_dseparated(m.COLLIDER, ["X"], ["Y"], ["Z"]) and \
        _ci_deviation(jc, oc, ["X"], ["Y"], ["Z"]) > DIP, \
        "condizionando sul collider Z X e Y diventano numericamente dipendenti: " \
        "is_dseparated deve dire False"
    assert not m.is_dseparated(m.COLLIDER, ["X"], ["Y"], ["W"]) and \
        _ci_deviation(jc, oc, ["X"], ["Y"], ["W"]) > DIP, \
        "condizionando sul discendente W del collider X e Y sono ancora " \
        "dipendenti: is_dseparated deve dire False"

    # --- rete Student, tutte le coppie e tutti i condizionamenti ---
    js, os_ = m.enumerate_joint(m.STUDENT, m.STUDENT_CARDS, seed=7)
    np.testing.assert_allclose(js.sum(), 1.0, rtol=1e-6, atol=1e-9)
    nodi = sorted(m.STUDENT)
    for x, y in itertools.combinations(nodi, 2):
        resto = [n for n in nodi if n not in (x, y)]
        for Z in _subsets(resto):
            dev = _ci_deviation(js, os_, [x], [y], Z)
            sep = m.is_dseparated(m.STUDENT, [x], [y], Z)
            if sep:
                assert dev < IND, \
                    (f"is_dseparated dice che {x} _|_ {y} | {Z}, ma nella "
                     f"congiunta vera la violazione e' {dev:.2e}: falso positivo")
            else:
                assert dev > DIP, \
                    (f"is_dseparated dice che {x} e {y} restano dipendenti dato "
                     f"{Z}, ma numericamente sono indipendenti ({dev:.2e}): "
                     f"cammino attivo inesistente")


# ----------------------------------------------------------------------
# 13-14: validazione e casi limite
# ----------------------------------------------------------------------

def test_implies_independence_validazione():
    """L'alias semantico deve rifiutare argomenti mal formati."""
    S = m.STUDENT
    assert m.implies_independence(S, ["D"], ["I"], []) is True, \
        "deve restituire lo stesso verdetto di is_dseparated"
    assert m.implies_independence(S, ["D"], ["I"], ["G"]) is False, \
        "deve restituire lo stesso verdetto di is_dseparated"

    with pytest.raises(ValueError):
        m.implies_independence(S, ["D"], ["PIPPO"], [])
    with pytest.raises(ValueError):
        m.implies_independence(S, ["D"], ["I"], ["NONESISTE"])
    with pytest.raises(ValueError):
        m.implies_independence(S, ["D", "G"], ["I"], ["G"])   # X e Z si toccano
    with pytest.raises(ValueError):
        m.implies_independence(S, ["D"], ["D"], ["G"])        # X e Y si toccano

    # su input validi deve coincidere con is_dseparated ovunque
    nodi = sorted(S)
    for x, y in itertools.combinations(nodi, 2):
        resto = [n for n in nodi if n not in (x, y)]
        for Z in _subsets(resto):
            assert m.implies_independence(S, [x], [y], Z) == \
                m.is_dseparated(S, [x], [y], Z), \
                f"implies_independence diverge da is_dseparated su {x},{y}|{Z}"


def test_casi_limite():
    """Grafi degeneri: un nodo solo, nessun arco, insiemi vuoti."""
    assert m.markov_blanket(DISCONNECTED, "A") == set(), \
        "senza archi il blanket e' vuoto"
    assert m.is_dseparated(DISCONNECTED, ["A"], ["B"], []), \
        "due nodi senza cammini fra loro sono sempre d-separati"
    assert m.active_paths(DISCONNECTED, "A", "B", []) == [], \
        "nessun cammino nello scheletro => nessun cammino attivo"
    assert m.is_dseparated(m.STUDENT, [], ["D", "I"], []), \
        "con X vuoto la d-separazione e' vacuamente vera"
    assert m.is_dseparated(m.STUDENT, ["D"], [], ["G"]), \
        "con Y vuoto la d-separazione e' vacuamente vera"
    assert m.ancestors(SINGLE, ["A"]) == {"A"}, \
        "An di un nodo isolato e' il nodo stesso"
    assert m.children(DISCONNECTED, "A") == [] and \
        m.parents(DISCONNECTED, "A") == [], \
        "un nodo isolato non ha ne' genitori ne' figli"
