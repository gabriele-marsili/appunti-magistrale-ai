import random 
import copy

man_pref = {
    1: [2, 3, 1, 4],
    2: [3, 4, 2, 1],
    3: [2, 1, 4, 3],
    4: [3, 1, 4, 2],
}

woman_pref = {
    1: [3, 2, 4, 1],
    2: [2, 4, 1, 3],
    3: [1, 4, 2, 3],
    4: [3, 2, 1, 4],
}


def man_courtship_algo(man_p: dict, woman_p: dict) -> dict:
    res = {}
    uomini_non_matchati = list(man_p.keys())
    woman_receiver_proposal = {}
    for w in woman_p.keys():  # initialization
        woman_receiver_proposal[w] = []
        res[w] = None

    while len(uomini_non_matchati) > 0:
        print("\n")
        for w in woman_p.keys():  # initialization
            woman_receiver_proposal[w] = []

        # man propongono a woman (->woman ricevono proposte)
        for m in uomini_non_matchati:
            m_arr = man_p[m]
            if len(m_arr) > 1:
                prop = m_arr.pop(0)
            else: # => last preference
                prop = m_arr[0]
                
            woman_receiver_proposal[prop].append(m)
            print(f"Woman {prop} ha ricevuto proposta da {m}")

        # donne scelgono il preferito tra le proposte ricevute
        for w in woman_receiver_proposal.keys():
            arr_proposte = woman_receiver_proposal[w]

            if len(arr_proposte) > 0:  # se la donna ha proposte
                if res[w]:  # aggiunge current res alle proposte
                    arr_proposte.append(res[w])

                print(f"arr prop woman {w} : {arr_proposte}")

                # donna sceglie in base a proprie preferenze
                preferenza_index = len(woman_p[w]) + 1
                current_marito = preferenza_index
                for proposta in arr_proposte:  # scorro le preferenze
                    idx = woman_p[w].index(proposta)
                    if idx < preferenza_index:
                        preferenza_index = idx
                        current_marito = proposta

                        if res[w] is not None and res[w] not in uomini_non_matchati:
                            uomini_non_matchati.append(res[w])
                            print(f"uomo {res[w]} cambiato (rifiutato)")
                            

                        print(f"woman {w} ha cambiato {res[w]} con {current_marito} in res")
                        res[w] = current_marito
                        uomini_non_matchati.remove(current_marito)

                    elif proposta not in uomini_non_matchati:
                        uomini_non_matchati.append(proposta)
                        print(f"uomo {proposta} rifiutato da donna {w}")

    return res


def calcola_soddifazione(m_p:dict, w_p:dict, ris:dict) -> tuple[dict,dict] : 
    #ris => donna : uomo
    lenght = len(m_p[1])
    if lenght > 1 :
        peso_soddisfazione =  1/(lenght-1) 
    else :
        peso_soddisfazione = 1/lenght

    peso_soddisfazione = peso_soddisfazione*100
    #print(f"peso s : {peso_soddisfazione}")
    ris_m = {}
    ris_w = {}

    for w in ris:
        m = ris[w]
        #print(f"coppia w:{w} m:{m}")
        index_pref_m = m_p[m].index(w)
        index_pref_w = w_p[w].index(m)
        #print(f"index_pref_m {index_pref_m}")
        #print(f"index_pref_w {index_pref_w}")
        

        s_m = 100 - index_pref_m * peso_soddisfazione
        s_w = 100 - index_pref_w * peso_soddisfazione
        #print(f"s_m {s_m}")
        #print(f"s_w {s_w}")


        ris_m[m] = round(s_m,2)
        ris_w[w] = round(s_w,2)

    return (ris_m, ris_w)


def fake_pref(original_sat_man:dict,original_sat_w:dict,m_p:dict, w_p:dict, all=False, max_iter = 1000, no_worst=False):
    it = 0
    max = len(w_p.keys())

    while it < max_iter : 
        it+=1
        quantity = random.randint(1,max) # |-> quantità di donne che fanno fake su proprie pref 
        chosable = []

        for i in range(1,max+1):
            chosable.append(i)

        order = []            
        w_p_copy = copy.deepcopy(w_p)
        m_p_copy = copy.deepcopy(m_p)
        for i in range(0,quantity):
            r = random.choice(chosable)
            chosable.remove(r)
            order.append(r)

        for i in order:
            random.shuffle(w_p_copy[i])

        new_ris = man_courtship_algo(m_p_copy,w_p_copy)
        (new_s_m, new_s_w) = calcola_soddifazione(m_p, w_p, new_ris) # calcolo rispetto a pref originali w_p anziché w_p_copy che son pref fake (?)

        #controllo:
        passed = False
        p_no_worst = 0
        at_least_one_better = False
        p = 0
        for w in new_s_w:

            if not all and no_worst and new_s_w[w] >= original_sat_w[w]: # Nessuna peggiora
                p_no_worst += 1

            if new_s_w[w] > original_sat_w[w]:
                at_least_one_better = True

            if all and new_s_w[w] > original_sat_w[w]:
                p+=1

            

        if no_worst:
            # Passa solo se TUTTE le donne sono >= e ALMENO UNA è >
            passed = (p_no_worst == max) and at_least_one_better
        elif all:
            # Passa solo se TUTTE le donne sono strettamente >
            passed = (p_no_worst == max) and (p == max)
        else:
            # Basta che almeno una sia > 
            passed = at_least_one_better

        if passed:
            cambiamenti_s_m = []
            cambiamenti_s_w = []
            for w in new_s_w:
                s = f"woman {w} da {original_sat_w[w]} a {new_s_w[w]} cambiando pref da {w_p[w]} a {w_p_copy[w]}"
                cambiamenti_s_w.append(s)

            for m in new_s_m:
                s = f"man {m} da {original_sat_man[m]} a {new_s_m[m]}"
                cambiamenti_s_m.append(s)

            res = {
                "new_ris" : new_ris,
                "original_sat_man": original_sat_man,
                "original_sat_w": original_sat_w,
                "new_s_m":new_s_m,
                "new_s_w":new_s_w,
                "cambiamenti_s_m":cambiamenti_s_m,
                "cambiamenti_s_w":cambiamenti_s_w,
                "order":order,
                "quantity":quantity,
            }

            return res

    return {"max iter reached" : max_iter}

        
            


def main():
    m_p = {
        1: [1,2,3,4],
        2: [4,2,3,1],
        3: [4,3,1,2],
        4: [1,4,3,2],
    }
    m_p_copy = copy.deepcopy(m_p)

    w_p = {
        1: [2,3,1,4],
        2: [3,1,2,4],
        3: [4,1,2,3],
        4: [1,4,2,3],
    }

    r = man_courtship_algo(m_p, w_p)
    print(f"Result:\n{r}")

    (s_m, s_w) = calcola_soddifazione(m_p_copy, w_p, r)
    print(f"Soddisfazione uomini:\n{s_m}")
    print(f"Soddisfazione donne:\n{s_w}")

    
    ris_f_p = fake_pref(s_m, s_w, m_p_copy, w_p, False, 500000, True)
    print("\nFake response:\n")
    for k in ris_f_p.keys():
        valore = ris_f_p[k]
        if isinstance(valore, list):
            print(f"{k}")
            for el in valore:
                print(el)
        else:
            print(f"{k}:\n{valore}")


if __name__ == "__main__": 
    main()