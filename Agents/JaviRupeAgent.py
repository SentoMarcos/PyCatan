# Importa módulos estándar
import random  # Para decisiones aleatorias
import json    # Para cargar y guardar datos en formato JSON
import os      # Para trabajar con rutas y archivos del sistema

# Importa constantes y clases definidas por el usuario
from Classes.Constants import *  # Constantes globales del juego
from Classes.Materials import Materials  # Clase que representa los recursos del jugador
from Classes.TradeOffer import TradeOffer  # Clase para representar una oferta de comercio
from Interfaces.AgentInterface import AgentInterface  # Interfaz base que todo agente debe heredar

# Definición de la clase del agente JaviRupe
class JaviRupeAgent(AgentInterface):
    # Nombres simbólicos para cada gen del agente (para facilitar la interpretación)
    GENE_NAMES = [
        'prob_weight', 'diversity_weight', 'harbor_weight', 'rival_penalty', 
        'prob_pueblo', 'prob_ciudad', 'agresividad_ladron',
        'trade_aggressiveness', 'trade_defensiveness', 'discard_risk', 
        'thief_block_leader', 'devcard_usage', 'early_expansion', 'mid_blocking',
        'endgame_safety', 'resource_hoarding', 'combo_recognition'
    ]

    # Valores por defecto de los genes, determinan el comportamiento inicial del agente
    DEFAULT_GENES = [
        3.7, 4.1, 10.5, 1.4, 0.31, 0.65, 1.45,  # Genes originales
        1.0, 1.0, 0.5, 1.0, 0.5,               # Genes de comercio y desarrollo
        0.8, 1.2, 1.5, 0.7, 1.3                # Nuevos genes estratégicos
    ]

    def __init__(self, agent_id, genes=None):
        # Constructor del agente, recibe el ID del jugador y genes opcionales
        super().__init__(agent_id)  # Llama al constructor de la clase base
        self.genes = self._load_genes(genes)  # Carga genes personalizados o por defecto
        self.town_number = 0  # Número de pueblos colocados
        self.turn_count = 0  # Contador de turnos
        self.game_phase = 'early'  # Fase del juego (early, mid, endgame)
        self.threat_assessment = {}  # Diccionario de amenazas por jugador
        self.resource_targets = []  # Lista de recursos prioritarios según estrategia

        # Muestra los genes del agente al comenzar
        print(f"[JaviRupeAgent] Genes: {dict(zip(self.GENE_NAMES, self.genes))}")

        # Recursos preferidos para la carta Year of Plenty
        self.year_of_plenty_material_one = MaterialConstants.CEREAL
        self.year_of_plenty_material_two = MaterialConstants.MINERAL

    def _load_genes(self, genes):
        """Carga genes desde un archivo JSON, una lista o usa los genes por defecto"""
        if isinstance(genes, str) and os.path.isfile(genes):
            try:
                with open(genes, 'r') as f:
                    loaded = json.load(f)
                    if isinstance(loaded, dict) and 'genes' in loaded:
                        genes_list = loaded['genes']
                    elif isinstance(loaded, list):
                        genes_list = loaded
                    else:
                        genes_list = self.DEFAULT_GENES.copy()
            except Exception:
                genes_list = self.DEFAULT_GENES.copy()
        else:
            genes_list = genes if genes is not None else self.DEFAULT_GENES.copy()

        # Asegura que la lista tenga la longitud correcta
        while len(genes_list) < len(self.DEFAULT_GENES):
            genes_list.append(self.DEFAULT_GENES[len(genes_list)])

        return genes_list

    def _update_game_state(self):
        """Actualiza el estado interno del juego, incluyendo la fase actual y amenazas"""
        self.turn_count += 1  # Aumenta el número de turnos jugados
        my_vp = getattr(self, 'victory_points', 0)  # Obtiene los puntos de victoria actuales

        # Establece la fase del juego según los puntos de victoria
        if my_vp < 4:
            self.game_phase = 'early'
        elif my_vp < 8:
            self.game_phase = 'mid'
        else:
            self.game_phase = 'endgame'

        # Analiza amenazas y recursos objetivo
        self._assess_threats()
        self._update_resource_targets()

    def _assess_threats(self):
        """Evalúa a los oponentes para determinar cuán peligrosos son"""
        self.threat_assessment = {}
        if not hasattr(self.board, 'players'):
            return  # Si no hay jugadores en el tablero, salir

        for i, player in enumerate(self.board.players):
            if i == self.id:
                continue  # No evaluarse a sí mismo

            threat_level = 0  # Valor de amenaza acumulado
            vp = player.get('victory_points', 0)
            resources = sum(player.get('resources', [0]*5))  # Suma total de recursos del jugador

            # Evaluación según puntos de victoria
            if vp >= 9:
                threat_level += 100  # Muy peligroso
            elif vp >= 7:
                threat_level += 50  # Medio
            elif vp >= 5:
                threat_level += 20  # Leve

            # Evaluación por acumulación de recursos
            if resources >= 10:
                threat_level += 30
            elif resources >= 7:
                threat_level += 15

            # Evaluación por posición en el tablero
            position_bonus = self._evaluate_player_position(i)
            threat_level += position_bonus

            # Guarda la evaluación de amenaza del jugador
            self.threat_assessment[i] = threat_level

    def _evaluate_player_position(self, player_id):
        """Asigna una puntuación basada en la ubicación del jugador en el tablero"""
        score = 0
        for node_id, node in enumerate(self.board.nodes):
            if node['player'] == player_id:
                # Evalúa la probabilidad de los terrenos conectados
                prob_sum = sum(self.board.terrain[t]['probability'] 
                               for t in node['contacting_terrain'])
                score += prob_sum * 0.5

                # Da puntos extra si el nodo tiene puerto
                if node['harbor'] != HarborConstants.NONE:
                    score += 5

        return min(score, 25)  # Limita el puntaje para evitar sobreestimación

    def _update_resource_targets(self):
        """Actualiza los recursos objetivo según la fase del juego"""
        self.resource_targets = []
        
        if self.game_phase == 'early':
            # Prioridad: expansión (madera, ladrillo, cereal, lana)
            self.resource_targets = [
                MaterialConstants.WOOD, MaterialConstants.CLAY,
                MaterialConstants.CEREAL, MaterialConstants.WOOL
            ]
        elif self.game_phase == 'mid':
            # Prioridad: ciudades y cartas de desarrollo
            self.resource_targets = [
                MaterialConstants.CEREAL, MaterialConstants.MINERAL,
                MaterialConstants.WOOL
            ]
        else:  # endgame
            # Prioridad: lo que necesites para ganar
            if self.hand.resources.has_most_of(BuildConstants.CITY):
                self.resource_targets = [MaterialConstants.CEREAL, MaterialConstants.MINERAL]
            else:
                self.resource_targets = [
                    MaterialConstants.CEREAL, MaterialConstants.CLAY,
                    MaterialConstants.WOOD, MaterialConstants.WOOL
                ]

    def _genetic_node_score(self, node_id):
        """Puntuación genética mejorada para nodos"""
        if node_id >= len(self.board.nodes):
            return 0
            
        node = self.board.nodes[node_id]
        terrains = node['contacting_terrain']
        
        # Suma de probabilidades ponderada
        prob_sum = sum(self.board.terrain[t]['probability'] for t in terrains)
        prob_score = prob_sum * self.genes[0]
        
        # Diversidad de recursos
        terrain_types = [self.board.terrain[t]['terrain_type'] 
                        for t in terrains 
                        if self.board.terrain[t]['terrain_type'] != TerrainConstants.DESERT]
        diversity_score = len(set(terrain_types)) * self.genes[1]
        
        # Bonus por puerto
        harbor_score = 0
        if (self.board.is_coastal_node(node_id) and 
            node['harbor'] != HarborConstants.NONE):
            harbor_score = self.genes[2]
            
        # Bonus por recursos objetivo
        target_bonus = 0
        for terrain_id in terrains:
            terrain_type = self.board.terrain[terrain_id]['terrain_type']
            if terrain_type in self.resource_targets:
                target_bonus += 2
        
        # Penalización por rivales cercanos
        rival_penalty = 0
        for adj_node in node['adjacent']:
            if (adj_node < len(self.board.nodes) and 
                self.board.nodes[adj_node]['player'] not in [-1, self.id]):
                rival_player = self.board.nodes[adj_node]['player']
                threat = self.threat_assessment.get(rival_player, 0)
                rival_penalty += self.genes[3] * (1 + threat * 0.01)
        
        # Bonus por fase del juego
        phase_bonus = 0
        if self.game_phase == 'early':
            # En early game, priorizar madera y ladrillo
            wood_brick_count = sum(1 for t in terrains 
                                 if self.board.terrain[t]['terrain_type'] 
                                 in [MaterialConstants.WOOD, MaterialConstants.CLAY])
            phase_bonus = wood_brick_count * self.genes[12]
        
        return (prob_score + diversity_score + harbor_score + 
                target_bonus + phase_bonus - rival_penalty)

    def on_trade_offer(self, board_instance, offer=TradeOffer(), player_making_offer=int):
        """Decisión de comercio mejorada"""
        # Rechazar inmediatamente si ayuda a un jugador peligroso
        if player_making_offer in self.threat_assessment:
            if self.threat_assessment[player_making_offer] > 70:
                return False
        
        # Análisis básico: ¿recibo más de lo que doy?
        if offer.receives.has_more(offer.gives):
            return True
        
        # ¿Me ayuda a completar una construcción importante?
        constructions = [BuildConstants.CITY, BuildConstants.TOWN, BuildConstants.CARD]
        my_resources_after = Materials(
            self.hand.resources.cereal + offer.receives.cereal - offer.gives.cereal,
            self.hand.resources.mineral + offer.receives.mineral - offer.gives.mineral,
            self.hand.resources.clay + offer.receives.clay - offer.gives.clay,
            self.hand.resources.wood + offer.receives.wood - offer.gives.wood,
            self.hand.resources.wool + offer.receives.wool - offer.gives.wool
        )
        
        for construction in constructions:
            if my_resources_after.has_more(construction):
                # En endgame, solo acepta si es crítico
                if self.game_phase == 'endgame':
                    my_vp = getattr(self, 'victory_points', 0)
                    if my_vp >= 8 and construction == BuildConstants.CITY:
                        return True
                    elif my_vp >= 7:
                        return True
                else:
                    return True
        
        return False

    def on_commerce_phase(self):
        """Fase de comercio mejorada"""
        self._update_game_state()
        
        # En endgame, ser muy conservador
        if self.game_phase == 'endgame':
            my_vp = getattr(self, 'victory_points', 0)
            if my_vp >= 8 and random.random() < self.genes[8] * 1.5:
                return None
        
        # Obtener puertos propios
        my_ports = []
        for node_id, node in enumerate(self.board.nodes):
            if (node['player'] == self.id and 
                node['harbor'] != HarborConstants.NONE):
                my_ports.append(node['harbor'])
        
        # Contar recursos
        counts = [self.hand.resources.get_from_id(i) for i in range(5)]
        max_mat = counts.index(max(counts))
        min_mat = counts.index(min(counts))
        
        # Estrategia 1: Comercio con puerto 2:1
        for port in my_ports:
            if (port < len(counts) and counts[port] >= 2 and 
                random.random() < self.genes[7]):
                gives = [0] * 5
                gives[port] = 2
                receives = [0] * 5
                
                # Pedir recurso que más necesito
                if self.resource_targets:
                    target = next((r for r in self.resource_targets if counts[r] < 2), 
                                min_mat)
                else:
                    target = min_mat
                    
                receives[target] = 1
                return TradeOffer(Materials(*gives), Materials(*receives))
        
        # Estrategia 2: Comercio de exceso
        if (counts[max_mat] >= 4 and counts[min_mat] <= 1 and 
            random.random() < self.genes[7]):
            
            # Verificar que no ayudamos a jugadores peligrosos
            dangerous_players = [p for p, threat in self.threat_assessment.items() 
                               if threat > 50]
            if len(dangerous_players) >= 2:  # Muchos jugadores peligrosos
                return None
            
            gives = [0] * 5
            gives[max_mat] = 3
            receives = [0] * 5
            receives[min_mat] = 1
            
            return TradeOffer(Materials(*gives), Materials(*receives))
        
        return None

    def on_having_more_than_7_materials_when_thief_is_called(self):
        """Descarte mejorado basado en objetivos"""
        self._update_game_state()
        # Identificar recursos críticos según objetivos actuales
        critical_resources = set()
        # Sustituir has_most_of por has_more (comprueba si puede construir)
        if self.hand.resources.has_more(BuildConstants.CITY):
            critical_resources.update([MaterialConstants.CEREAL, MaterialConstants.MINERAL])
        if self.hand.resources.has_more(BuildConstants.TOWN):
            critical_resources.update([MaterialConstants.CEREAL, MaterialConstants.CLAY, 
                                     MaterialConstants.WOOD, MaterialConstants.WOOL])
        if self.hand.resources.has_more(BuildConstants.ROAD):
            critical_resources.update([MaterialConstants.CLAY, MaterialConstants.WOOD])
        # Orden de descarte: menos crítico primero
        discard_priority = [
            MaterialConstants.WOOL,    # Menos versátil
            MaterialConstants.MINERAL, # Solo para ciudades y cartas
            MaterialConstants.CLAY,    # Para caminos y pueblos
            MaterialConstants.WOOD,    # Para caminos y pueblos
            MaterialConstants.CEREAL   # Más versátil
        ]
        while self.hand.get_total() > 7:
            # Descarta primero lo que no es crítico
            for mat in discard_priority:
                if mat not in critical_resources and self.hand.resources.get_from_id(mat) > 0:
                    self.hand.remove_material(mat, 1)
                    break
            else:
                # Si solo quedan críticos, descarta el que más tengas
                counts = [self.hand.resources.get_from_id(i) for i in range(5)]
                max_mat = counts.index(max(counts))
                if counts[max_mat] > 0:
                    self.hand.remove_material(max_mat, 1)
                else:
                    break
        return self.hand

    def on_moving_thief(self):
        """Movimiento del ladrón con IA mejorada"""
        current_thief_terrain = -1
        best_move = None
        best_score = -1
        
        # Encontrar posición actual del ladrón
        for terrain in self.board.terrain:
            if terrain['has_thief']:
                current_thief_terrain = terrain['id']
                break
        
        # Evaluar cada posible movimiento
        for terrain in self.board.terrain:
            if terrain['has_thief'] or terrain['probability'] == 0:
                continue
                
            nodes = self.board.__get_contacting_nodes__(terrain['id'])
            affected_players = {}
            
            # Contar construcciones de cada jugador en este terreno
            for node_id in nodes:
                player = self.board.nodes[node_id]['player']
                if player != -1 and player != self.id:
                    if player not in affected_players:
                        affected_players[player] = 0
                    # Contar ciudades como 2, pueblos como 1
                    node = self.board.nodes[node_id]
                    building = node.get('building', None)
                    if building == BuildConstants.CITY:
                        affected_players[player] += 2
                    elif building == BuildConstants.TOWN:
                        affected_players[player] += 1
            
            # Calcular puntuación para este movimiento
            for player, impact in affected_players.items():
                threat = self.threat_assessment.get(player, 0)
                prob_impact = terrain['probability']
                
                # Priorizar según amenaza del jugador
                if threat > 80:  # Amenaza crítica
                    score = 1000 + prob_impact * 10 + impact * 20
                elif threat > 50:  # Amenaza alta
                    score = 500 + prob_impact * 5 + impact * 10
                else:  # Amenaza normal
                    score = prob_impact + impact * 2
                
                # Bonus por probabilidad alta del terreno
                if prob_impact in [6, 8]:
                    score += 20
                elif prob_impact in [5, 9]:
                    score += 10
                
                if score > best_score:
                    best_move = {'terrain': terrain['id'], 'player': player}
                    best_score = score
        
        return best_move if best_move else {'terrain': current_thief_terrain, 'player': -1}

    def on_turn_start(self):
        """Inicio de turno con uso inteligente de cartas"""
        self._update_game_state()
        
        # Uso estratégico de cartas de desarrollo
        if random.random() < self.genes[11]:
            # Priorizar según fase del juego
            if self.game_phase == 'endgame':
                # En endgame, usar cartas agresivamente
                for i, card in enumerate(self.development_cards_hand.hand):
                    if card.type == DevelopmentCardConstants.VICTORY_POINT:
                        my_vp = getattr(self, 'victory_points', 0)
                        if my_vp >= 9:  # Ganar inmediatamente
                            return self.development_cards_hand.select_card(i)
                    elif card.effect in [DevelopmentCardConstants.MONOPOLY_EFFECT,
                                       DevelopmentCardConstants.YEAR_OF_PLENTY_EFFECT]:
                        return self.development_cards_hand.select_card(i)
            
            # Usar caballero si el ladrón nos afecta
            for i, card in enumerate(self.development_cards_hand.hand):
                if card.type == DevelopmentCardConstants.KNIGHT:
                    if self._thief_affects_me():
                        return self.development_cards_hand.select_card(i)
        
        return None

    def _thief_affects_me(self):
        """Verifica si el ladrón actual nos afecta"""
        for terrain in self.board.terrain:
            if terrain['has_thief']:
                nodes = self.board.__get_contacting_nodes__(terrain['id'])
                for node_id in nodes:
                    if self.board.nodes[node_id]['player'] == self.id:
                        return True
        return False

    def on_game_start(self, board_instance):
        """Inicio del juego con colocación estratégica optimizada"""
        self.board = board_instance
        possibilities = self.board.valid_starting_nodes()
        
        if not possibilities:
            return -1, -1
        
        # Usar puntuación genética para elegir el mejor nodo inicial
        best_node = max(possibilities, key=self._genetic_node_score)
        self.town_number += 1
        
        # Elegir camino inicial estratégicamente
        possible_roads = self.board.nodes[best_node]['adjacent']
        best_road = possible_roads[0] if possible_roads else -1
        
        # Priorizar expansión hacia puertos o bloqueo de rivales
        road_scores = {}
        for adj_node in possible_roads:
            score = 0
            
            # Bonus por puerto
            if (self.board.is_coastal_node(adj_node) and 
                self.board.nodes[adj_node]['harbor'] != HarborConstants.NONE):
                score += 15
            
            # Bonus por buenos nodos futuros
            score += self._genetic_node_score(adj_node) * 0.5
            
            # Penalización si hay rivales muy cerca
            rival_count = sum(1 for n in self.board.nodes[adj_node]['adjacent']
                            if (n < len(self.board.nodes) and 
                                self.board.nodes[n]['player'] not in [-1, self.id]))
            score -= rival_count * 5
            
            road_scores[adj_node] = score
        
        if road_scores:
            best_road = max(road_scores.keys(), key=lambda x: road_scores[x])
        
        return best_node, best_road

    def on_build_phase(self, board_instance):
        """Fase de construcción con IA estratégica mejorada"""
        self.board = board_instance
        self._update_game_state()
        
        my_vp = getattr(self, 'victory_points', 0)
        
        # PRIORIDAD 1: Ganar inmediatamente si es posible
        if my_vp >= 9:
            if self.hand.resources.has_more(BuildConstants.CITY):
                possibilities = self.board.valid_city_nodes(self.id)
                if possibilities:
                    # Elegir la ciudad más segura
                    safest = self._find_safest_node(possibilities)
                    self.town_number -= 1
                    return {'building': BuildConstants.CITY, 'node_id': safest}
            
            if self.hand.resources.has_more(BuildConstants.TOWN):
                possibilities = self.board.valid_town_nodes(self.id)
                if possibilities:
                    safest = self._find_safest_node(possibilities)
                    self.town_number += 1
                    return {'building': BuildConstants.TOWN, 'node_id': safest}
        
        # PRIORIDAD 2: Bloquear jugadores que pueden ganar
        critical_threat = max(self.threat_assessment.values()) if self.threat_assessment else 0
        if critical_threat > 90:
            blocking_move = self._find_blocking_move()
            if blocking_move:
                return blocking_move
        
        # PRIORIDAD 3: Construcción estratégica normal
        
        # Ciudades: Mejor ROI de recursos
        if (self.hand.resources.has_more(BuildConstants.CITY) and 
            self.town_number > 0 and 
            random.random() > self.genes[5]):  # prob_ciudad
            
            possibilities = self.board.valid_city_nodes(self.id)
            if possibilities:
                best_city = max(possibilities, key=self._genetic_node_score)
                self.town_number -= 1
                return {'building': BuildConstants.CITY, 'node_id': best_city}
        
        # Pueblos: Expansión y puntos
        if (self.hand.resources.has_more(BuildConstants.TOWN) and 
            random.random() > self.genes[4]):  # prob_pueblo
            
            possibilities = self.board.valid_town_nodes(self.id)
            if possibilities:
                if self.game_phase == 'endgame':
                    # En endgame, priorizar seguridad
                    best_town = self._find_safest_node(possibilities)
                else:
                    # En early/mid, priorizar recursos
                    best_town = max(possibilities, key=self._genetic_node_score)
                
                self.town_number += 1
                return {'building': BuildConstants.TOWN, 'node_id': best_town}
        
        # Caminos: Conectividad y bloqueo
        if self.hand.resources.has_more(BuildConstants.ROAD):
            possibilities = self.board.valid_road_nodes(self.id)
            if possibilities:
                best_road = self._choose_best_road(possibilities)
                if best_road:
                    return {
                        'building': BuildConstants.ROAD,
                        'node_id': best_road['starting_node'],
                        'road_to': best_road['finishing_node']
                    }
        
        # Cartas de desarrollo: Inversión a futuro
        if (self.hand.resources.has_more(BuildConstants.CARD) and 
            random.random() < self.genes[11] and  # devcard_usage
            self.game_phase != 'early'):  # No en early game
            
            return {'building': BuildConstants.CARD}
        
        return None

    def _find_safest_node(self, nodes):
        """Encuentra el nodo más seguro de una lista"""
        if not nodes:
            return None
            
        safety_scores = {}
        for node in nodes:
            safety = 0
            
            # Contar rivales cercanos
            rival_count = 0
            for adj in self.board.nodes[node]['adjacent']:
                if (adj < len(self.board.nodes) and 
                    self.board.nodes[adj]['player'] not in [-1, self.id]):
                    rival_count += 1
            
            safety -= rival_count * 10
            
            # Bonus por estar lejos de jugadores peligrosos
            for player_id, threat in self.threat_assessment.items():
                if threat > 70:
                    distance = self._calculate_distance_to_player(node, player_id)
                    safety += distance * 5
            
            # Bonus por recursos
            safety += self._genetic_node_score(node) * 0.3
            
            safety_scores[node] = safety
        
        return max(safety_scores.keys(), key=lambda x: safety_scores[x])

    def _calculate_distance_to_player(self, node, player_id):
        """Calcula distancia aproximada a las construcciones de un jugador"""
        player_nodes = [i for i, n in enumerate(self.board.nodes) 
                       if n['player'] == player_id]
        if not player_nodes:
            return 10  # Muy lejos si no tiene construcciones
        
        # Distancia mínima (aproximada) 
        min_distance = min(abs(node - pn) for pn in player_nodes)
        return min(min_distance, 10)

    def _find_blocking_move(self):
        """Encuentra un movimiento para bloquear jugadores peligrosos"""
        # Identificar el jugador más peligroso
        if not self.threat_assessment:
            return None
            
        most_dangerous = max(self.threat_assessment.keys(), 
                           key=lambda x: self.threat_assessment[x])
        
        # Intentar bloquear con pueblo si es posible
        if self.hand.resources.has_more(BuildConstants.TOWN):
            possibilities = self.board.valid_town_nodes(self.id)
            blocking_nodes = []
            
            for node in possibilities:
                # ¿Este nodo bloquea la expansión del jugador peligroso?
                dangerous_adjacent = any(
                    self.board.nodes[adj]['player'] == most_dangerous
                    for adj in self.board.nodes[node]['adjacent']
                    if adj < len(self.board.nodes)
                )
                
                if dangerous_adjacent:
                    blocking_nodes.append(node)
            
            if blocking_nodes:
                best_block = max(blocking_nodes, key=self._genetic_node_score)
                self.town_number += 1
                return {'building': BuildConstants.TOWN, 'node_id': best_block}
        
        return None

    def _choose_best_road(self, possibilities):
        """Elige la mejor carretera para construir, evitando usar dicts como clave"""
        road_scores = []
        for road in possibilities:
            node = road['finishing_node']
            terrains = self.board.nodes[node]['contacting_terrain']
            prob = sum(self.board.terrain[t]['probability'] for t in terrains)
            harbor_bonus = self.genes[2] if self.board.is_coastal_node(node) and self.board.nodes[node]['harbor'] != HarborConstants.NONE else 0
            block_bonus = 0
            for p in getattr(self.board, 'players', []):
                if p.get('victory_points', 0) >= 8 and node in [adj for n in self.board.valid_town_nodes(p.get('id', -1)) for adj in self.board.nodes[n]['adjacent']]:
                    block_bonus += 15
                if p.get('victory_points', 0) == 9 and node in [adj for n in self.board.nodes if self.board.nodes[n]['player'] == p.get('id', -1) for adj in self.board.nodes[n]['adjacent']]:
                    block_bonus += 30
            if self.board.nodes[node]['player'] == -1:
                score = prob + harbor_bonus + self._genetic_node_score(node) + block_bonus
            else:
                score = -100
            road_scores.append((road, score))
        if not road_scores:
            return None
        best_road, _ = max(road_scores, key=lambda x: x[1])
        return best_road

    def on_turn_end(self):
        """Final del turno - usar cartas de victoria si es posible"""
        my_vp = getattr(self, 'victory_points', 0)
        
        for i, card in enumerate(self.development_cards_hand.hand):
            if (card.type == DevelopmentCardConstants.VICTORY_POINT and 
                my_vp + 1 >= 10):
                return self.development_cards_hand.select_card(i)
        
        return None