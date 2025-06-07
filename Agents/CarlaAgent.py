import random
from Classes.Constants import *
from Classes.Materials import Materials
from Classes.TradeOffer import TradeOffer
from Interfaces.AgentInterface import AgentInterface

class CarlaAgent(AgentInterface):
    town_number = 0
    material_given_more_than_three = None
    board = 0

    def __init__(self, agent_id):
        super().__init__(agent_id)

    def on_trade_offer(self, board_instance, offer=TradeOffer(), player_making_offer=int):
        if offer.gives.has_more(offer.receives):
            return True
        else:
            return False

    def on_commerce_phase(self):
        if self.material_given_more_than_three is not None:
            if len(self.development_cards_hand.hand):
                for i in range(0, len(self.development_cards_hand.hand)):
                    if self.development_cards_hand.hand[i].effect == DevelopmentCardConstants.MONOPOLY_EFFECT:
                        return self.development_cards_hand.select_card(i)

        gives = Materials(0,0,0,0,0)
        receives = Materials(0,0,0,0,0)

        if self.town_number >= 1 and self.hand.resources.has_more(BuildConstants.CITY):
            self.material_given_more_than_three = None
            return None

        elif self.town_number >= 1:
            cereal_hand = self.hand.resources.cereal
            mineral_hand = self.hand.resources.mineral
            wood_hand = self.hand.resources.wood
            clay_hand = self.hand.resources.clay
            wool_hand = self.hand.resources.wool
            total_given_materials = (2 - cereal_hand) + (3 - mineral_hand)

            if total_given_materials < (wood_hand + clay_hand + wool_hand):
                materials_to_give = [0, 0, 0, 0, 0]
                for i in range(0, total_given_materials):
                    order = [MaterialConstants.CLAY, MaterialConstants.WOOD, MaterialConstants.WOOL]
                    random.shuffle(order)
                    for mat in order:
                        if self.hand.resources.get_from_id(mat) > 0:
                            self.hand.remove_material(mat, 1)
                            materials_to_give[mat] += 1
                            break
                gives = Materials(*materials_to_give)
            else:
                gives = Materials(0, 0, clay_hand, wood_hand, wool_hand)

            receives = Materials(2, 3, 0, 0, 0)

        elif self.town_number == 0:
            if self.hand.resources.has_more(Materials(1, 0, 1, 1, 1)):
                return None
            else:
                materials_to_receive = [1 - self.hand.resources.cereal,
                                        0 - self.hand.resources.mineral,
                                        1 - self.hand.resources.clay,
                                        1 - self.hand.resources.wood,
                                        1 - self.hand.resources.wool]
                materials_to_give = [0, 0, 0, 0, 0]
                number_of_materials_received = 0

                for i in range(5):
                    if materials_to_receive[i] <= 0:
                        materials_to_receive[i] = 0
                    else:
                        number_of_materials_received += 1

                for j in range(0, number_of_materials_received):
                    order = [MaterialConstants.CEREAL, MaterialConstants.MINERAL, MaterialConstants.CLAY,
                             MaterialConstants.WOOD, MaterialConstants.WOOL]
                    random.shuffle(order)
                    for mat in order:
                        if self.hand.resources.get_from_id(mat) > 1 or mat == MaterialConstants.MINERAL:
                            self.hand.remove_material(mat, 1)
                            materials_to_give[mat] += 1
                            break

                gives = Materials(*materials_to_give)
                receives = Materials(*materials_to_receive)

        trade_offer = TradeOffer(gives, receives)
        return trade_offer

    def on_game_start(self, board_instance):
        self.board = board_instance
        possibilities = self.board.valid_starting_nodes()

        chosen_node_id = -1
        chosen_road_to_id = -1

        for node_id in possibilities:
            if node_id in self.board.nodes and 'adjacent' in self.board.nodes[node_id]:
                for adj_node_id in self.board.nodes[node_id]['adjacent']:
                    if adj_node_id in self.board.nodes and 'number' in self.board.nodes[adj_node_id]:
                        if self.board.terrain[self.board.nodes[adj_node_id]['terrain']]['probability'] in [6, 8]:
                            adjacent_numbers = [self.board.nodes[adj_node_id]['number'] for adj_node_id in self.board.nodes[node_id]['adjacent']]
                            closest_to_7 = min(adjacent_numbers, key=lambda x: abs(x - 7))
                            if closest_to_7 not in [self.board.nodes[adj_node_id]['number'] for adj_node_id in self.board.nodes[node_id]['adjacent']]:
                                chosen_node_id = node_id
                                break

        if chosen_node_id == -1 and possibilities:
            chosen_node_id = random.choice(possibilities)

        self.town_number += 1

        if chosen_node_id in self.board.nodes and 'adjacent' in self.board.nodes[chosen_node_id]:
            possible_roads = self.board.nodes[chosen_node_id]['adjacent']
            chosen_road_to_id = random.choice(possible_roads)

        return chosen_node_id, chosen_road_to_id

    def on_turn_start(self):
        if self.development_cards_hand:
            for i in range(0, len(self.development_cards_hand.hand)):
                if self.development_cards_hand.hand[i].type == DevelopmentCardConstants.KNIGHT:
                    return self.development_cards_hand.select_card(i)
        return None

    def on_build_phase(self, board_instance):
        self.board = board_instance

        if len(self.development_cards_hand.hand):
            for i, card in enumerate(self.development_cards_hand.hand):
                if (card.effect == DevelopmentCardConstants.YEAR_OF_PLENTY_EFFECT or
                        card.effect == DevelopmentCardConstants.ROAD_BUILDING_EFFECT):
                    return self.development_cards_hand.select_card(i)

        if self.hand.resources.has_more(BuildConstants.CITY) and self.town_number > 0:
            city_nodes = self.board.valid_city_nodes(self.id)
            for node_id in city_nodes:
                for terrain_id in self.board.nodes[node_id]['contacting_terrain']:
                    probability = self.board.terrain[terrain_id]['probability']
                    if probability in [5, 6, 8, 9]:
                        self.town_number -= 1
                        return {'building': BuildConstants.CITY, 'node_id': node_id}

        if self.hand.resources.has_more(BuildConstants.TOWN):
            town_nodes = self.board.valid_town_nodes(self.id)
            for node_id in town_nodes:
                for terrain_id in self.board.nodes[node_id]['contacting_terrain']:
                    probability = self.board.terrain[terrain_id]['probability']
                    if probability in [4, 5, 6, 8, 9, 10]:
                        self.town_number += 1
                        return {'building': BuildConstants.TOWN, 'node_id': node_id}

        if self.hand.resources.has_more(BuildConstants.ROAD):
            road_nodes = self.board.valid_road_nodes(self.id)
            for road_obj in road_nodes:
                if self.board.is_coastal_node(road_obj['finishing_node']) and \
                self.board.nodes[road_obj['finishing_node']]['harbor'] != HarborConstants.NONE:
                    return {'building': BuildConstants.ROAD,
                            'node_id': road_obj['starting_node'],
                            'road_to': road_obj['finishing_node']}

            if random.random() < 0.6 and len(road_nodes) > 0:
                road_obj = random.choice(road_nodes)
                return {'building': BuildConstants.ROAD,
                        'node_id': road_obj['starting_node'],
                        'road_to': road_obj['finishing_node']}

        if self.hand.resources.has_more(BuildConstants.CARD):
            return {'building': BuildConstants.CARD}

        return None

    def on_turn_end(self):
        if len(self.development_cards_hand.hand):
            for i in range(0, len(self.development_cards_hand.hand)):
                if self.development_cards_hand.hand[i].type == DevelopmentCardConstants.VICTORY_POINT:
                    return self.development_cards_hand.select_card(i)
        return None

    def on_having_more_than_7_materials_when_thief_is_called(self):
        hand_resources = self.hand.resources
        total_excess = self.hand.get_total() - 7
        if total_excess <= 0:
            return self.hand

        while self.hand.get_total() > 7:
            available_indices = [idx for idx, count in enumerate(self.hand.resources) if count > 0]
            if not available_indices:
                break
            idx_to_discard = random.choice(available_indices)
            self.hand.remove_material(idx_to_discard, 1)

        return self.hand

    def on_moving_thief(self):
        terrain_with_thief_id = -1
        for terrain in self.board.terrain:
            if not terrain['has_thief']:
                if terrain['probability'] == 6 or terrain['probability'] == 8:
                    nodes = self.board.__get_contacting_nodes__(terrain['id'])
                    has_own_town = False
                    has_enemy_town = False
                    enemy = -1
                    for node_id in nodes:
                        if self.board.nodes[node_id]['player'] == self.id:
                            has_own_town = True
                            break
                        if self.board.nodes[node_id]['player'] != -1:
                            has_enemy_town = True
                            enemy = self.board.nodes[node_id]['player']
                    if not has_own_town and has_enemy_town:
                        return {'terrain': terrain['id'], 'player': enemy}
            else:
                terrain_with_thief_id = terrain['id']

        return {'terrain': terrain_with_thief_id, 'player': -1}

    def on_monopoly_card_use(self):
        # Estrategia simple: elegir el recurso más común entre todos los jugadores si se pudiera saber (por ahora aleatorio)
        resource_to_call = random.choice([
            MaterialConstants.CEREAL,
            MaterialConstants.CLAY,
            MaterialConstants.MINERAL,
            MaterialConstants.WOOD,
            MaterialConstants.WOOL
        ])
        return resource_to_call