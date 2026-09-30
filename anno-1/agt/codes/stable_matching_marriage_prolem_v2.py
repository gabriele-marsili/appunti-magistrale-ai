from __future__ import annotations

from collections import deque
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from itertools import combinations, permutations, product
from typing import Literal, TypeAlias


# ============================================================
# TYPES
# ============================================================

PreferenceMap: TypeAlias = Mapping[int, Sequence[int]]
Mode: TypeAlias = Literal["any", "pareto", "all"]
Score: TypeAlias = tuple[int, int, int]


@dataclass(frozen=True)
class PreferenceChange:
    true: list[int]
    fake: list[int]


@dataclass
class SearchResult:
    found: bool
    mode: Mode
    checked_profiles: int
    message: str | None

    manipulators: list[int]
    fake_preferences: dict[int, list[int]]
    changed_preferences: dict[int, PreferenceChange]

    original_matching: dict[int, int]
    new_matching: dict[int, int] | None

    original_women_satisfaction: dict[int, float]
    new_women_satisfaction: dict[int, float] | None

    original_men_satisfaction: dict[int, float]
    new_men_satisfaction: dict[int, float] | None

    rank_gain: dict[int, int] | None
    satisfaction_gain: dict[int, float] | None


# ============================================================
# VALIDATION
# ============================================================

def validate_preferences(
    men_pref: PreferenceMap,
    women_pref: PreferenceMap,
) -> None:
    """Verifica che le preferenze descrivano un'istanza completa 1-a-1."""

    men = set(men_pref.keys())
    women = set(women_pref.keys())

    if len(men) != len(women):
        raise ValueError("Il numero di uomini e donne deve coincidere.")

    for m, pref in men_pref.items():
        if len(pref) != len(women) or set(pref) != women:
            raise ValueError(
                f"Preferenze non valide per l'uomo {m}: "
                "devono contenere ogni donna esattamente una volta."
            )

    for w, pref in women_pref.items():
        if len(pref) != len(men) or set(pref) != men:
            raise ValueError(
                f"Preferenze non valide per la donna {w}: "
                "devono contenere ogni uomo esattamente una volta."
            )


# ============================================================
# GALE-SHAPLEY: MEN PROPOSE
# ============================================================

def gale_shapley(
    men_pref: PreferenceMap,
    women_reported_pref: PreferenceMap,
) -> dict[int, int]:
    """
    Gale-Shapley con gli uomini come proposer.

    Le preferenze passate alla funzione NON vengono modificate.
    Restituisce un dizionario {donna: uomo}.
    """

    women_rank: dict[int, dict[int, int]] = {
        w: {m: rank for rank, m in enumerate(pref)}
        for w, pref in women_reported_pref.items()
    }

    free_men: deque[int] = deque(men_pref.keys())

    next_proposal: dict[int, int] = {
        m: 0 for m in men_pref
    }

    husband: dict[int, int | None] = {
        w: None for w in women_reported_pref
    }

    while free_men:
        m = free_men.popleft()

        proposal_index = next_proposal[m]

        if proposal_index >= len(men_pref[m]):
            raise RuntimeError(
                f"L'uomo {m} ha esaurito tutte le possibili proposte."
            )

        w = men_pref[m][proposal_index]
        next_proposal[m] = proposal_index + 1

        current = husband[w]

        if current is None:
            husband[w] = m
            continue

        if women_rank[w][m] < women_rank[w][current]:
            husband[w] = m
            free_men.append(current)
        else:
            free_men.append(m)

    result: dict[int, int] = {}

    for w, m in husband.items():
        if m is None:
            raise RuntimeError("Matching incompleto.")
        result[w] = m

    return result


# ============================================================
# UTILITY / SODDISFAZIONE
# ============================================================

def build_rank(pref: PreferenceMap) -> dict[int, dict[int, int]]:
    """rank[x][y] = posizione di y nelle preferenze di x."""

    return {
        x: {y: index for index, y in enumerate(order)}
        for x, order in pref.items()
    }


def rank_to_satisfaction(rank: int, n: int) -> float:
    """
    Con n = 4:
        rank 0 -> 100.00
        rank 1 ->  66.67
        rank 2 ->  33.33
        rank 3 ->   0.00
    """

    if n <= 0:
        raise ValueError("n deve essere positivo.")

    if n == 1:
        return 100.0

    return round(
        100.0 * (n - 1 - rank) / (n - 1),
        2,
    )


def calculate_satisfaction(
    true_men_pref: PreferenceMap,
    true_women_pref: PreferenceMap,
    matching: Mapping[int, int],
) -> tuple[dict[int, float], dict[int, float]]:
    """
    Calcola la soddisfazione rispetto alle preferenze VERE.

    matching è nel formato {donna: uomo}.
    """

    n = len(true_men_pref)

    men_rank = build_rank(true_men_pref)
    women_rank = build_rank(true_women_pref)

    men_sat: dict[int, float] = {}
    women_sat: dict[int, float] = {}

    for w, m in matching.items():
        men_sat[m] = rank_to_satisfaction(men_rank[m][w], n)
        women_sat[w] = rank_to_satisfaction(women_rank[w][m], n)

    return men_sat, women_sat


# ============================================================
# CONTROLLO DEL MIGLIORAMENTO
# ============================================================

def improvement_condition(
    gains: Mapping[int, int],
    mode: Mode,
) -> bool:
    """
    gains[w] > 0  -> donna w migliorata
    gains[w] = 0  -> invariata
    gains[w] < 0  -> peggiorata

    mode="any":
        almeno una donna migliora; le altre possono peggiorare.

    mode="pareto":
        almeno una donna migliora e nessuna peggiora.

    mode="all":
        tutte le donne migliorano strettamente.
    """

    values = tuple(gains.values())

    if mode == "any":
        return any(g > 0 for g in values)

    if mode == "pareto":
        return all(g >= 0 for g in values) and any(g > 0 for g in values)

    # Grazie a Literal, a questo punto mode può essere solo "all".
    return all(g > 0 for g in values)


# ============================================================
# RICERCA FAKE PREFERENCES
# ============================================================

def find_fake_preferences(
    men_pref: PreferenceMap,
    women_true_pref: PreferenceMap,
    mode: Mode = "any",
    require_liar_improves: bool = False,
    find_best: bool = True,
) -> SearchResult:
    """
    Cerca sistematicamente fake preferences delle donne.

    La ricerca prova prima una sola manipolatrice, poi due, ecc.
    In questo modo la prima cardinalità per cui viene trovata una
    soluzione è il numero minimo di donne che devono mentire.

    Se find_best=True, fra le soluzioni con il minimo numero di
    manipolatrici viene scelta quella con score migliore.
    """

    validate_preferences(men_pref, women_true_pref)

    women = list(women_true_pref.keys())
    n = len(women)

    # --------------------------------------------------------
    # BASELINE TRUTHFUL
    # --------------------------------------------------------

    base_matching = gale_shapley(men_pref, women_true_pref)

    base_men_sat, base_women_sat = calculate_satisfaction(
        men_pref,
        women_true_pref,
        base_matching,
    )

    true_women_rank = build_rank(women_true_pref)

    base_rank: dict[int, int] = {
        w: true_women_rank[w][base_matching[w]]
        for w in women
    }

    # --------------------------------------------------------
    # TUTTE LE FALSE PREFERENZE POSSIBILI PER OGNI DONNA
    # --------------------------------------------------------

    fake_orders: dict[int, list[tuple[int, ...]]] = {}

    for w in women:
        original = tuple(women_true_pref[w])

        fake_orders[w] = [
            perm
            for perm in permutations(original)
            if perm != original
        ]

    checked_profiles = 0

    best_result: SearchResult | None = None
    best_score: Score | None = None

    # --------------------------------------------------------
    # PROVO PRIMA 1 MANIPOLATRICE, POI 2, ..., n
    # --------------------------------------------------------

    for number_of_liars in range(1, n + 1):
        found_at_this_level = False

        for liars_tuple in combinations(women, number_of_liars):
            liars = list(liars_tuple)

            possible_fake_profiles = product(
                *(fake_orders[w] for w in liars)
            )

            for fake_values in possible_fake_profiles:
                checked_profiles += 1

                # Copia mutabile delle preferenze vere.
                reported_pref: dict[int, list[int]] = {
                    w: list(pref)
                    for w, pref in women_true_pref.items()
                }

                # Le sole donne in liars dichiarano preferenze false.
                for w, fake_pref in zip(liars, fake_values):
                    reported_pref[w] = list(fake_pref)

                # Matching calcolato sulle preferenze DICHIARATE.
                matching = gale_shapley(men_pref, reported_pref)

                # Valutazione fatta sulle preferenze VERE.
                new_rank: dict[int, int] = {
                    w: true_women_rank[w][matching[w]]
                    for w in women
                }

                # Rank più piccolo = partner migliore.
                # Quindi old_rank - new_rank > 0 significa miglioramento.
                gains: dict[int, int] = {
                    w: base_rank[w] - new_rank[w]
                    for w in women
                }

                if not improvement_condition(gains, mode):
                    continue

                if require_liar_improves and not any(
                    gains[w] > 0 for w in liars
                ):
                    continue

                found_at_this_level = True

                new_men_sat, new_women_sat = calculate_satisfaction(
                    men_pref,
                    women_true_pref,
                    matching,
                )

                sat_gain_women: dict[int, float] = {
                    w: round(
                        new_women_sat[w] - base_women_sat[w],
                        2,
                    )
                    for w in women
                }

                changed_preferences: dict[int, PreferenceChange] = {
                    w: PreferenceChange(
                        true=list(women_true_pref[w]),
                        fake=list(reported_pref[w]),
                    )
                    for w in liars
                }

                candidate = SearchResult(
                    found=True,
                    mode=mode,
                    checked_profiles=checked_profiles,
                    message=None,
                    manipulators=liars.copy(),
                    fake_preferences={
                        w: list(reported_pref[w])
                        for w in women
                    },
                    changed_preferences=changed_preferences,
                    original_matching=base_matching.copy(),
                    new_matching=matching.copy(),
                    original_women_satisfaction=base_women_sat.copy(),
                    new_women_satisfaction=new_women_sat.copy(),
                    original_men_satisfaction=base_men_sat.copy(),
                    new_men_satisfaction=new_men_sat.copy(),
                    rank_gain=gains.copy(),
                    satisfaction_gain=sat_gain_women.copy(),
                )

                if not find_best:
                    return candidate

                score: Score = (
                    sum(1 for gain in gains.values() if gain > 0),
                    sum(gains.values()),
                    min(gains.values()),
                )

                if best_score is None or score > best_score:
                    best_score = score
                    best_result = candidate

        # Se è stata trovata almeno una soluzione con k manipolatrici,
        # non serve passare a k+1: vogliamo minimizzare il loro numero.
        if found_at_this_level:
            if best_result is None:
                raise RuntimeError(
                    "Stato interno incoerente: soluzione trovata ma risultato assente."
                )

            best_result.checked_profiles = checked_profiles
            return best_result

    return SearchResult(
        found=False,
        mode=mode,
        checked_profiles=checked_profiles,
        message="Nessuna manipolazione soddisfa il criterio richiesto.",
        manipulators=[],
        fake_preferences={},
        changed_preferences={},
        original_matching=base_matching.copy(),
        new_matching=None,
        original_women_satisfaction=base_women_sat.copy(),
        new_women_satisfaction=None,
        original_men_satisfaction=base_men_sat.copy(),
        new_men_satisfaction=None,
        rank_gain=None,
        satisfaction_gain=None,
    )


# ============================================================
# OUTPUT
# ============================================================

def print_result(result: SearchResult) -> None:
    if not result.found:
        print("\nNESSUNA SOLUZIONE")
        print(result.message or "Nessuna soluzione trovata.")
        print(f"Profili controllati: {result.checked_profiles}")
        return

    # Type narrowing esplicito per Pylance e controllo runtime.
    if (
        result.new_matching is None
        or result.new_women_satisfaction is None
        or result.new_men_satisfaction is None
        or result.rank_gain is None
        or result.satisfaction_gain is None
    ):
        raise RuntimeError("Risultato marcato come trovato ma incompleto.")

    print("\n" + "=" * 60)
    print("FAKE PREFERENCES TROVATE")
    print("=" * 60)

    print(f"\nModalità: {result.mode}")
    print(f"Donne che mentono: {result.manipulators}")

    print("\nPreferenze modificate:")

    for w, change in result.changed_preferences.items():
        print(f"\nWoman {w}")
        print(f"  vera : {change.true}")
        print(f"  fake : {change.fake}")

    print("\nMatching originale:")
    print(result.original_matching)

    print("\nNuovo matching:")
    print(result.new_matching)

    print("\nSoddisfazione donne:")

    for w in result.original_women_satisfaction:
        old = result.original_women_satisfaction[w]
        new = result.new_women_satisfaction[w]
        gain = result.satisfaction_gain[w]

        symbol = "↑" if gain > 0 else "↓" if gain < 0 else "="

        print(
            f"  Woman {w}: "
            f"{old:6.2f} -> {new:6.2f} "
            f"{symbol} ({gain:+.2f})"
        )

    print("\nSoddisfazione uomini:")

    for m in result.original_men_satisfaction:
        old = result.original_men_satisfaction[m]
        new = result.new_men_satisfaction[m]
        gain = round(new - old, 2)

        symbol = "↑" if gain > 0 else "↓" if gain < 0 else "="

        print(
            f"  Man {m}: "
            f"{old:6.2f} -> {new:6.2f} "
            f"{symbol} ({gain:+.2f})"
        )

    print(f"\nProfili controllati: {result.checked_profiles}")


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    men_pref: dict[int, list[int]] = {
        1: [1, 2, 3, 4],
        2: [4, 2, 3, 1],
        3: [4, 3, 1, 2],
        4: [1, 4, 3, 2],
    }

    women_pref: dict[int, list[int]] = {
        1: [2, 3, 1, 4],
        2: [3, 1, 2, 4],
        3: [4, 1, 2, 3],
        4: [1, 4, 2, 3],
    }

    # --------------------------------------------------------
    # POSSIBILI MODALITÀ:
    #
    # mode="any"
    #   -> almeno una donna migliora; altre possono peggiorare.
    #
    # mode="pareto"
    #   -> almeno una migliora e nessuna peggiora.
    #
    # mode="all"
    #   -> tutte migliorano strettamente.
    #
    # require_liar_improves=True
    #   -> almeno una delle donne che mente deve migliorare.
    # --------------------------------------------------------

    result = find_fake_preferences(
        men_pref,
        women_pref,
        mode="pareto",
        require_liar_improves=False,
        find_best=True,
    )

    print_result(result)


if __name__ == "__main__":
    main()
