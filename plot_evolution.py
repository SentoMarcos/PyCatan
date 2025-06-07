import json
import matplotlib.pyplot as plt
import numpy as np

# Cargar historial de evolución
def load_history(filename='evolution_history.json'):
    with open(filename, 'r') as f:
        history = json.load(f)
    return history

def plot_evolution(history):
    generations = [h['generation'] for h in history]
    best_scores = [h['score'] for h in history]
    mean_scores = [h['mean_score'] for h in history]
    genes = np.array([h['genes'] for h in history])

    plt.figure(figsize=(12, 6))
    plt.subplot(2, 1, 1)
    plt.plot(generations, best_scores, label='Mejor fitness', color='green')
    plt.plot(generations, mean_scores, label='Media fitness', color='blue', alpha=0.5)
    plt.xlabel('Generación')
    plt.ylabel('Fitness')
    plt.title('Evolución del fitness')
    plt.legend()
    plt.grid(True)

    plt.subplot(2, 1, 2)
    for i in range(genes.shape[1]):
        plt.plot(generations, genes[:, i], label=f'Gen {i+1}')
    plt.xlabel('Generación')
    plt.ylabel('Valor de los genes óptimos')
    plt.title('Evolución de los genes óptimos')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    history = load_history()
    plot_evolution(history)
