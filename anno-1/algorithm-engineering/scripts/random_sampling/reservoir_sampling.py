import matplotlib.pyplot as plt
import random as r

def r_sampling(n, k):
    """
    O(k) spazio, O(n) tempo, n/B I/O
    prob: k/(i+1)
    """
    res = []
    for i in range(n):
        # Riempiamo il reservoir con i primi k elementi
        if i < k:
            res.append(i)
        else:
            # Scegliamo un indice casuale j tra 0 e i (inclusi)
            j = r.randint(0, i)
            # Se j è minore della dimensione del reservoir (k), 
            # sostituiamo l'elemento
            if j < k:
                res[j] = i
    return res

def compute_distribution():
    distribution = {}
    times = 10000  # Aumentato per ridurre il rumore nel grafico
    n = 1000
    k = 10
    
    for _ in range(times):
        res = r_sampling(n, k)
        for el in res:
            if el in distribution:
                distribution[el] += 1
            else:
                distribution[el] = 1  # Corretto da 0 a 1
                
    return distribution, n, k, times

def plot_distribution(distribution, n, k, times):
    # Prepariamo i dati per il grafico (garantendo che ci siano tutti gli elementi da 0 a n-1)
    elementi = list(range(n))
    frequenze = [distribution.get(el, 0) for el in elementi]
    
    # Calcolo della frequenza attesa: (k / n) * numero_di_iterazioni
    frequenza_attesa = (k / n) * times
    
    # Creazione del grafico
    plt.figure(figsize=(12, 6))
    plt.bar(elementi, frequenze, color='skyblue', width=1.0, alpha=0.8)
    
    # Linea della frequenza attesa ideale
    plt.axhline(y=frequenza_attesa, color='red', linestyle='--', linewidth=2, 
                label=f'Frequenza attesa ideale ({frequenza_attesa})')
    
    plt.title("Distribuzione degli elementi con Reservoir Sampling", fontsize=14)
    plt.xlabel("Valore dell'elemento (0 - 999)", fontsize=12)
    plt.ylabel("Numero di estrazioni", fontsize=12)
    plt.legend()
    plt.grid(axis='y', linestyle=':', alpha=0.7)
    
    # Mostriamo il grafico
    plt.show()

# Esecuzione principale
if __name__ == "__main__":
    print("Calcolo della distribuzione in corso...")
    dist, n, k, times = compute_distribution()
    print("Generazione del grafico...")
    plot_distribution(dist, n, k, times)