import json
import random
import subprocess
import time
import os
import glob
from pathlib import Path

# Configuración
POPULATION_SIZE = 40
GENERATIONS = 150  # Referencia, el bucle está limitado por tiempo
GAMES_PER_AGENT = 15  # Más partidas por individuo para robustez
AGENT_PATH = 'Agents.JaviRupeAgent.JaviRupeAgent'
OTHER_AGENTS = [
    'Agents.CrabisaAgent.CrabisaAgent',
    'Agents.EdoAgent.EdoAgent',
    'Agents.SigmaAgent.SigmaAgent',
    'Agents.RandomAgent.RandomAgent',
    'Agents.PabloAleixAlexAgent.PabloAleixAlexAgent',
    'Agents.AlexPelochoJaimeAgent.AlexPelochoJaimeAgent',
    'Agents.CarlesZaidaAgent.CarlesZaidaAgent',
    'Agents.TristanAgent.TristanAgent',
    'Agents.AlexPastorAgent.AlexPastorAgent',
    'Agents.AdrianHerasAgent.AdrianHerasAgent',
]
GENE_BOUNDS = [
    (2.0, 6.0),   # prob
    (2.0, 6.0),   # div
    (5.0, 15.0),  # puerto
    (0.5, 2.5),   # penal_rival
    (0.1, 0.7),   # prob_pueblo
    (0.1, 0.9),   # prob_ciudad
    (0.5, 2.0)    # agresividad_ladron
]
RESULTS_FILE = 'best_genes.json'
HISTORY_FILE = 'evolution_history.json'
ELITISM = 3  # Número de mejores individuos que pasan sin cambios
RANDOM_INDIVIDUALS = 2  # Individuos completamente aleatorios por generación


def random_genes():
    return [random.uniform(a, b) for a, b in GENE_BOUNDS]

def mutate_genes(genes):
    idx = random.randint(0, len(genes)-1)
    new_genes = genes[:]
    a, b = GENE_BOUNDS[idx]
    new_genes[idx] = min(max(new_genes[idx] + random.uniform(-0.2, 0.2), a), b)
    return new_genes

def crossover(g1, g2):
    return [(a if random.random() < 0.5 else b) for a, b in zip(g1, g2)]

def run_games(genes, agent_idx, gen):
    # Crea un archivo único por generación e individuo
    genes_file = f'genes_{gen}_{agent_idx}.json'
    with open(genes_file, 'w') as f:
        json.dump(genes, f)
    total_partial_wins = 0
    total_points = 0
    total_margin = 0
    total_first_places = 0
    total_second_places = 0
    total_last_places = 0
    total_penalty_random = 0
    total_point_diff = 0
    rivals = [a for a in OTHER_AGENTS]
    random.shuffle(rivals)
    rival_groups = [rivals[i:i+3] for i in range(0, len(rivals), 3)]
    for group in rival_groups:
        if len(group) < 3:
            group = group + random.sample(OTHER_AGENTS, 3-len(group))
        agents = [f'{AGENT_PATH}:{genes_file}'] + group
        cmd = ['python', 'main.py', '--agents'] + agents + ['--games', str(GAMES_PER_AGENT)]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=1200)
            lines = result.stdout.splitlines()
            my_idx = agents.index(f'{AGENT_PATH}:{genes_file}')
            # Buscar victorias parciales
            win_line = None
            for i, line in enumerate(lines):
                if 'Victorias por jugador:' in line:
                    win_line = lines[i+1+my_idx]
                    break
            if win_line:
                wins = int(win_line.split(':')[1].split()[0])
                total_partial_wins += wins
            # Buscar el índice real del agente optimizado
            my_player_idx = None
            for line in lines:
                if genes_file in line and line.strip().startswith('P'):
                    try:
                        my_player_idx = int(line.split(':')[0].replace('P','').strip())
                        break
                    except Exception as e:
                        print(f"DEBUG PLAYER IDX ERROR: {e} | line: {line}")
            if my_player_idx is None:
                print(f"DEBUG: No se encontró el índice de jugador para {genes_file}")
                continue
            # Buscar puntos y posiciones finales
            points = None
            positions = []
            for line in lines:
                if 'victory_points' in line and 'P' in line:
                    try:
                        pidx = int(line.split('P')[1].split()[0])
                        pts = int(line.split(':')[1].split()[0])
                        positions.append((pidx, pts))
                        if pidx == my_player_idx:
                            points = pts
                    except Exception as e:
                        print(f"DEBUG PARSER ERROR: {e} | line: {line}")
                        continue
            print(f"DEBUG: positions={positions}, points={points}, my_player_idx={my_player_idx}, total_first_places={total_first_places}, total_last_places={total_last_places}")
            if points is not None:
                total_points += points
            # Calcular posición final y diferencia de puntos
            if positions:
                positions.sort(key=lambda x: x[1], reverse=True)
                my_points = [pts for pidx, pts in positions if pidx == my_player_idx]
                if my_points:
                    my_points = my_points[0]
                    my_rank = 1 + sum(1 for _, pts in positions if pts > my_points)
                    if my_rank == 1:
                        total_first_places += 1
                        # Diferencia de puntos con el segundo
                        if len(positions) > 1:
                            total_point_diff += my_points - positions[1][1]
                    elif my_rank == 2:
                        total_second_places += 1
                    elif my_rank == len(positions):
                        total_last_places += 1
            # Penaliza perder contra RandomAgent
            if any('RandomAgent' in r for r in group):
                random_idx = [i for i, r in enumerate(group) if 'RandomAgent' in r]
                for ridx in random_idx:
                    random_points = [pts for pidx, pts in positions if pidx == ridx+1]  # +1 porque P0 es el agente optimizado
                    if points is not None and random_points and points < random_points[0]:
                        total_penalty_random += 1
        except Exception as e:
            print(f'Error running games: {e}')
    # Fitness competitivo:
    fitness = (
        30 * total_first_places +    # Subido para premiar la victoria
        10 * total_second_places +   # Subido para premiar la constancia
        (2 * total_point_diff) +     # Doble peso a la diferencia de puntos
        (total_points / max(1, len(rival_groups))) / 10 -
        15 * total_last_places -     # Penalización más fuerte por quedar último
        40 * total_penalty_random    # Penalización mucho más fuerte por perder contra RandomAgent
    )
    return fitness

def main():
    start_time = time.time()
    max_seconds = 0.5 * 60 * 60  # 8 horas
    # Si hay genes previos, usarlos como semilla
    try:
        with open('best_genes.json', 'r') as f:
            best_prev = json.load(f)
            if isinstance(best_prev, dict) and 'genes' in best_prev:
                seed_genes = best_prev['genes']
            else:
                seed_genes = None
    except Exception:
        seed_genes = None
    population = [random_genes() for _ in range(POPULATION_SIZE)]
    if seed_genes:
        population[0] = seed_genes
    best_score = -1
    best_genes = seed_genes if seed_genes else None
    history = []
    gen = 0
    last_best_score = -1
    stagnation_counter = 0
    max_stagnation = 5  # Generaciones permitidas con retroceso o sin mejora
    last_improvement_time = start_time
    while time.time() - start_time < max_seconds:
        gen += 1
        # Limpia archivos de genes antiguos para evitar confusión
        for f in glob.glob('genes_*.json'):
            try:
                os.remove(f)
            except Exception:
                pass
        elapsed = time.time() - start_time
        elapsed_min = int(elapsed // 60)
        elapsed_sec = int(elapsed % 60)
        # Estimación de tiempo restante
        gens_left = GENERATIONS - gen if GENERATIONS else 0
        avg_gen_time = elapsed / gen if gen > 0 else 0
        est_remaining = max_seconds - elapsed
        est_remaining_min = int(est_remaining // 60)
        est_remaining_sec = int(est_remaining % 60)
        print(f'\nGeneración {gen} | Tiempo transcurrido: {elapsed_min}m {elapsed_sec}s | Tiempo estimado restante: {est_remaining_min}m {est_remaining_sec}s')
        scores = []
        for idx, genes in enumerate(population):
            print(f'  Evaluando individuo {idx+1}/{POPULATION_SIZE}')
            score = run_games(genes, idx, gen)
            scores.append((genes, score))
            if score > best_score:
                best_score = score
                best_genes = genes
                last_improvement_time = time.time()
                print(f'\033[92m[MEJORA] Nueva mejor puntuación: {best_score:.2f} con genes: {best_genes} (individuo {idx+1})\033[0m')
        # Elitismo: top N pasan sin cambios
        scores.sort(key=lambda x: x[1], reverse=True)
        next_pop = [s[0] for s in scores[:ELITISM]]
        # Diversidad: añade algunos individuos aleatorios
        for _ in range(RANDOM_INDIVIDUALS):
            next_pop.append(random_genes())
        # Rellenar con mutaciones y cruces
        while len(next_pop) < POPULATION_SIZE:
            if random.random() < 0.8:
                g = crossover(random.choice(scores[:6])[0], random.choice(scores[:6])[0])
            else:
                g = mutate_genes(random.choice(scores[:6])[0])
            next_pop.append(g)
        population = next_pop
        mean_score = sum(s[1] for s in scores) / len(scores)
        print(f'Mejor genes generación: {scores[0][0]}, score: {scores[0][1]:.2f}, media: {mean_score:.2f}')
        print(f'Tiempo desde última mejora: {int((time.time()-last_improvement_time)//60)}m {int((time.time()-last_improvement_time)%60)}s')
        history.append({'generation': gen, 'genes': scores[0][0], 'score': scores[0][1], 'mean_score': mean_score})
        # Guardar progreso parcial
        with open(RESULTS_FILE, 'w') as f:
            json.dump({'genes': best_genes, 'score': best_score}, f)
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)
        # Guardar los peores genes de la generación para análisis
        with open('worst_genes.json', 'w') as f:
            json.dump({'genes': scores[-1][0], 'score': scores[-1][1], 'generation': gen}, f)
        # Parar si hay retroceso o decrecimiento
        if last_best_score != -1 and scores[0][1] < last_best_score:
            stagnation_counter += 1
            print(f'¡Advertencia! Retroceso detectado en la generación {gen}. ({stagnation_counter}/{max_stagnation})')
        else:
            stagnation_counter = 0
        last_best_score = scores[0][1]
        if stagnation_counter >= max_stagnation:
            print('Entrenamiento detenido por retroceso/decrecimiento. Guardando mejores genes.')
            break
    total_elapsed = time.time() - start_time
    print(f'Entrenamiento finalizado tras {gen} generaciones y {int(total_elapsed//60)} minutos {int(total_elapsed%60)} segundos.')
    print(f'Genes óptimos guardados en {RESULTS_FILE}: {best_genes} (Score: {best_score})')
    print(f'Historial de evolución guardado en {HISTORY_FILE}')

if __name__ == '__main__':
    main()
