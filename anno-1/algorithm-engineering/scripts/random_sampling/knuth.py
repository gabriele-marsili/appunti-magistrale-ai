import random 

def knuth(seq, k):
    sample = []
    n = len(seq)
    
    # Se chiediamo più elementi di quanti ne esistano, restituiamo tutta la sequenza
    if k >= n:
        return seq[:]
        
    r = n  # Elementi rimasti da esaminare
    
    for i in range(0, n):
        # 1. Controlliamo se dobbiamo prendere l'elemento corrente
        if random.random() < k / r:
            sample.append(seq[i])
            k -= 1  # Un elemento in meno da cercare
            
        # 2. Un elemento è stato esaminato, quindi i rimanenti diminuiscono SEMPRE
        r -= 1

        # 3. Ottimizzazione: se abbiamo preso tutti i k elementi, possiamo fermarci subito
        if k == 0:
            return sample
    
    return sample

# Test
test = [1, 2, 3, 4, 5, 6, 7, 8, 9]
for i in range(5):
    print(f"Knuth [{i}]: {knuth(test, 3)}")