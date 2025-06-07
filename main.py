import sys
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--agents', nargs='+', help='Lista de agentes (Agents.Modulo.Clase o Agents.Modulo.Clase:genes.json)')
    parser.add_argument('--games', type=int, help='Número de partidas a jugar')
    args, unknown = parser.parse_known_args()

    if args.agents and args.games:
        # Modo automático para entrenamiento
        import importlib
        def make_agent_wrapper(agent_class, arg=None):
            if arg:
                class AgentWithGenes(agent_class):
                    def __init__(self, agent_id):
                        print(f"[main.py] Instanciando {agent_class.__name__} con genes: {arg}")
                        super().__init__(agent_id, arg)
                return AgentWithGenes
            else:
                return agent_class
        agent_wrappers = []
        for agent_str in args.agents:
            if ':' in agent_str:
                class_path, arg = agent_str.split(':', 1)
            else:
                class_path, arg = agent_str, None
            parts = class_path.split('.')
            if len(parts) != 3:
                raise ValueError(f'Formato de agente incorrecto: {agent_str}')
            module = importlib.import_module(f"{parts[0]}.{parts[1]}")
            agent_class = getattr(module, parts[2])
            agent_wrappers.append(make_agent_wrapper(agent_class, arg))
        from Managers.GameDirector import GameDirector
        game_director = GameDirector(agents=agent_wrappers)
        games_to_play = args.games
        wins = [0, 0, 0, 0]
        print('--- Asignación de agentes a jugadores ---')
        for idx, agent_str in enumerate(args.agents):
            print(f'P{idx}: {agent_str}')
        for i in range(games_to_play):
            print('......')
            game_director.game_start(i + 1)
            players = game_director.game_manager.get_players()
            for idx, player in enumerate(players):
                if player['victory_points'] >= 10:
                    wins[idx] += 1
                    break
        print('------------------------')
        game_director.trace_loader.export_every_game_to_file()
        print('Victorias por jugador:')
        for idx, count in enumerate(wins):
            print(f'Jugador {idx}: {count} victorias')
        return

    from Managers.GameDirector import GameDirector
    game_director = GameDirector()
    try:
        games_to_play = int(input('Number of games to be played: '))
    except ValueError:
        games_to_play = 0
# Contador de victorias por jugador
    wins = [0, 0, 0, 0]
    if isinstance(games_to_play, int) and games_to_play > 0:
        for i in range(games_to_play):
            print('......')
            game_director.game_start(i + 1)
            # Determinar el ganador de la partida actual
            players = game_director.game_manager.get_players()
            for idx, player in enumerate(players):
                if player['victory_points'] >= 10:
                    wins[idx] += 1
                    break
            # Imprime los puntos finales de cada jugador tras cada partida
            for idx, player in enumerate(players):
                print(f'P{idx} victory_points: {player["victory_points"]}')
        print('------------------------')
        game_director.trace_loader.export_every_game_to_file()
        # Mostrar el contador de victorias
        print('Victorias por jugador:')
        for idx, count in enumerate(wins):
            print(f'Jugador {idx}: {count} victorias')
        return


if __name__ == '__main__':
    main()
