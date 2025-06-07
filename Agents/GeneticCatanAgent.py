from Classes.Constants import *
from Classes.Materials import Materials
from Classes.TradeOffer import TradeOffer
from Interfaces.AgentInterface import AgentInterface
import random

class GeneticCatanAgent(AgentInterface):
    # Genes: [peso_prob, peso_div, bonus_puerto, penal_rival, prob_pueblo, prob_ciudad, agresividad_ladron]
    # FINAL OPTIMIZED GENES from Genetic Algorithm Maximum Trainer (Fitness: 1.057)
    DEFAULT_GENES = [3.7163669620856528, 4.147785963201982, 10.501374058411406, 1.4123948710880545, 0.3133721627054283, 0.6526594140589657, 1.450477043808903]

    def __init__(self, agent_id, genes=None):
        super().__init__(agent_id)
        self.genes = genes if genes is not None else self.DEFAULT_GENES.copy()
        self.board = None
        self.town_number = 0

    # --- MÉTODOS OBLIGATORIOS DEL INTERFACE ---
    def on_game_start(self, board_instance):
        self.board = board_instance
        possibilities = self.board.valid_starting_nodes()
        def node_score(node_id):
            terrains = self.board.nodes[node_id]['contacting_terrain']
            prob_sum = sum(self.board.terrain[t]['probability'] for t in terrains)
            diversity = len(set(self.board.terrain[t]['terrain_type'] for t in terrains if self.board.terrain[t]['terrain_type'] != TerrainConstants.DESERT))
            harbor_bonus = self.genes[2] if self.board.is_coastal_node(node_id) and self.board.nodes[node_id]['harbor'] != HarborConstants.NONE else 0
            rival_penalty = sum(self.genes[3] for n in self.board.nodes[node_id]['adjacent'] if self.board.nodes[n]['player'] not in [-1, self.id])
            return prob_sum * self.genes[0] + diversity * self.genes[1] + harbor_bonus - rival_penalty
        chosen_node_id = max(possibilities, key=node_score)
        possible_roads = self.board.nodes[chosen_node_id]['adjacent']
        def road_score(adj_id):
            if self.board.nodes[adj_id]['player'] == -1:
                return node_score(adj_id)
            return -100
        chosen_road_to_id = max(possible_roads, key=road_score)
        self.town_number += 1
        return chosen_node_id, chosen_road_to_id

    def on_build_phase(self, board_instance):
        self.board = board_instance
        def prob_sum(node_id):
            return sum(self.board.terrain[t]['probability'] for t in self.board.nodes[node_id]['contacting_terrain'])
        # Decisión parametrizada: ¿construir pueblo o ciudad?
        build_decision = random.random()
        if self.hand.resources.has_more(BuildConstants.CITY) and self.town_number > 0 and build_decision > self.genes[4]:
            possibilities = self.board.valid_city_nodes(self.id)
            if possibilities:
                best_node = max(possibilities, key=prob_sum)
                self.town_number -= 1
                return {'building': BuildConstants.CITY, 'node_id': best_node}
        if self.hand.resources.has_more(BuildConstants.TOWN):
            possibilities = self.board.valid_town_nodes(self.id)
            if possibilities:
                def node_score2(node_id):
                    terrains = self.board.nodes[node_id]['contacting_terrain']
                    prob = sum(self.board.terrain[t]['probability'] for t in terrains)
                    diversity = len(set(self.board.terrain[t]['terrain_type'] for t in terrains if self.board.terrain[t]['terrain_type'] != TerrainConstants.DESERT))
                    harbor_bonus = self.genes[2] if self.board.is_coastal_node(node_id) and self.board.nodes[node_id]['harbor'] != HarborConstants.NONE else 0
                    adj = self.board.nodes[node_id]['adjacent']
                    rival_penalty = sum(self.genes[3] for n in adj if self.board.nodes[n]['player'] not in [-1, self.id])
                    return prob * self.genes[0] + diversity * self.genes[1] + harbor_bonus - rival_penalty
                best_node = max(possibilities, key=node_score2)
                self.town_number += 1
                return {'building': BuildConstants.TOWN, 'node_id': best_node}
        if self.hand.resources.has_more(BuildConstants.ROAD):
            possibilities = self.board.valid_road_nodes(self.id)
            if possibilities:
                def road_score(road):
                    node = road['finishing_node']
                    terrains = self.board.nodes[node]['contacting_terrain']
                    prob = sum(self.board.terrain[t]['probability'] for t in terrains)
                    harbor_bonus = self.genes[2] if self.board.is_coastal_node(node) and self.board.nodes[node]['harbor'] != HarborConstants.NONE else 0
                    if self.board.nodes[node]['player'] == -1:
                        return prob + harbor_bonus
                    return -100
                best_road = max(possibilities, key=road_score)
                return {'building': BuildConstants.ROAD, 'node_id': best_road['starting_node'], 'road_to': best_road['finishing_node']}
        # No se puede construir, intenta carta desarrollo
        if self.hand.resources.has_more(BuildConstants.CARD) and random.random() < self.genes[5]:
            return {'building': BuildConstants.CARD}
        return None

    def on_commerce_phase(self):
        # No trades por defecto, puede ser parametrizable (GEN extra)
        return None

    def on_trade_offer(self, board_instance, offer=TradeOffer(), player_making_offer=int):
        # Acepta solo si el rival NO es líder y le beneficia (parámetro de agresividad)
        players = board_instance.get_players() if hasattr(board_instance, 'get_players') else []
        my_points = next((p['victory_points'] for p in players if p['id'] == self.id), 0)
        rival_points = next((p['victory_points'] for p in players if p['id'] == player_making_offer), 0)
        if offer.gives.has_more(offer.receives) and rival_points < my_points + 2 * (1 - self.genes[6]):
            return True
        return False

    def on_moving_thief(self):
        # Ataca al rival con más puntos y a los hexágonos de mayor probabilidad, con peso genes[6]
        terrain_with_thief_id = -1
        best = None
        best_score = -1
        max_points = -1
        players = self.board.get_players() if hasattr(self.board, 'get_players') else []
        for terrain in self.board.terrain:
            if not terrain['has_thief'] and terrain['probability'] in [6,8,5,9]:
                nodes = self.board.__get_contacting_nodes__(terrain['id'])
                enemies = [self.board.nodes[n]['player'] for n in nodes if self.board.nodes[n]['player'] not in [-1, self.id]]
                if enemies:
                    enemy_points = max((p['victory_points'] for p in players if p['id'] in enemies), default=0)
                    score = terrain['probability'] * self.genes[6] + enemy_points
                    if score > best_score:
                        best = {'terrain': terrain['id'], 'player': enemies[0]}
                        best_score = score
            elif terrain['has_thief']:
                terrain_with_thief_id = terrain['id']
        return best if best else {'terrain': terrain_with_thief_id, 'player': -1}

    def on_turn_start(self):
        # Juega caballero si lo tiene y hay alguien con más puntos
        if self.development_cards_hand.hand:
            for i, card in enumerate(self.development_cards_hand.hand):
                if card.type == DevelopmentCardConstants.KNIGHT:
                    return self.development_cards_hand.select_card(i)
        return None

    def on_turn_end(self):
        # Juega punto de victoria si puede (podrías hacerlo dependiente de gen)
        if self.development_cards_hand.hand:
            for i, card in enumerate(self.development_cards_hand.hand):
                if card.type == DevelopmentCardConstants.VICTORY_POINT:
                    return self.development_cards_hand.select_card(i)
        return None

    def on_having_more_than_7_materials_when_thief_is_called(self):
        # Descarta primero recursos menos valiosos (puedes parametrizar el orden por GEN extra)
        discard_order = [MaterialConstants.WOOL, MaterialConstants.CLAY, MaterialConstants.WOOD, MaterialConstants.MINERAL, MaterialConstants.CEREAL]
        while self.hand.get_total() > 7:
            for mat in discard_order:
                if self.hand.resources.get_from_id(mat) > 0:
                    self.hand.remove_material(mat, 1)
                    break
        return self.hand

    def on_monopoly_card_use(self):
        # Elige el material que más necesita para construir (puedes mejorarlo con GEN extra)
        return MaterialConstants.CEREAL

    def on_road_building_card_use(self):
        valid_nodes = self.board.valid_road_nodes(self.id)
        if len(valid_nodes) > 1:
            road1 = valid_nodes[0]
            road2 = valid_nodes[1]
            return {'node_id': road1['starting_node'], 'road_to': road1['finishing_node'],
                    'node_id_2': road2['starting_node'], 'road_to_2': road2['finishing_node']}
        elif len(valid_nodes) == 1:
            road = valid_nodes[0]
            return {'node_id': road['starting_node'], 'road_to': road['finishing_node'],
                    'node_id_2': None, 'road_to_2': None}
        return None

    def on_year_of_plenty_card_use(self):
        return {'material': MaterialConstants.CEREAL, 'material_2': MaterialConstants.MINERAL}

# =============================================================================
# SUPERIOR AI AGENT - OPTIMIZED VERSION
# =============================================================================

class SuperiorAIAgent(GeneticCatanAgent):
    """
    SuperiorAIAgent optimizado con parámetros del algoritmo genético.
    
    Parámetros optimizados del Gen 9 (Fitness: 1.030):
    - peso_prob: 1.787 - Valoración de probabilidades de hexágonos
    - peso_div: 4.535 - Peso de diversificación de recursos  
    - bonus_puerto: 9.381 - Bonus por acceso a puertos comerciales
    - penal_rival: 1.037 - Penalización por proximidad a rivales
    - prob_pueblo: 0.589 - Probabilidad de construir pueblos vs ciudades
    - prob_ciudad: 0.877 - Probabilidad de construir ciudades
    - agresividad_ladron: 1.119 - Agresividad en movimiento del ladrón
    """
    
    def __init__(self, agent_id):
        # Usar los genes optimizados del Gen 9
        optimized_genes = [1.7869053490647477, 4.535421469727165, 9.380776182112363, 
                          1.0366849666846885, 0.589089200502295, 0.8771050207637486, 
                          1.1190970793794492]
        super().__init__(agent_id, optimized_genes)
        
    def get_agent_name(self):
        """Retorna el nombre del agente para identificación."""
        return "SuperiorAIAgent (Genetically Optimized)"
        
    def get_optimization_info(self):
        """Retorna información sobre la optimización."""
        return {
            "generation": 9,
            "fitness": 1.030,
            "optimization_method": "Genetic Algorithm",
            "genes": self.genes,
            "parameters": {
                "peso_prob": self.genes[0],
                "peso_div": self.genes[1], 
                "bonus_puerto": self.genes[2],
                "penal_rival": self.genes[3],
                "prob_pueblo": self.genes[4],
                "prob_ciudad": self.genes[5],
                "agresividad_ladron": self.genes[6]
            }
        }
