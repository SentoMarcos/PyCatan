import unittest
from Classes.Board import Board
from Classes.Constants import *


class TestBoard(unittest.TestCase):
    def test_build_town(self):
        board = Board()
        node = board.nodes[0]
        self.assertTrue(node['player'] == -1 and node['has_city'] is False)
        finishing_node = board.nodes[1]
        node['roads'].append({'player_id': 0, 'node_id': 1})
        finishing_node['roads'].append({'player_id': 0, 'node_id': 0})
        board.build_town(0, 0)
        self.assertTrue(node['player'] == 0 and node['has_city'] is False)
        finishing_node = board.nodes[8]
        node['roads'].append({'player_id': 2, 'node_id': 8})
        finishing_node['roads'].append({'player_id': 2, 'node_id': 0})
        board.build_town(2, 0)
        self.assertTrue(node['player'] != 2)
        node = board.nodes[1]
        board.build_town(0, 1)
        self.assertTrue(node['player'] == -1 and node['has_city'] is False)
        board.nodes[1]['roads'].append({'player_id': 0, 'node_id': 2})
        board.nodes[2]['roads'].append({'player_id': 0, 'node_id': 1})
        node = board.nodes[2]
        board.build_town(0, 2)
        self.assertTrue(node['player'] == 0 and node['has_city'] is False)

    def test_build_city(self):
        board = Board()
        node = board.nodes[0]
        self.assertTrue(node['player'] == -1 and node['has_city'] is False)
        finishing_node = board.nodes[1]
        node['roads'].append({'player_id': 0, 'node_id': 1})
        finishing_node['roads'].append({'player_id': 0, 'node_id': 0})
        board.build_city(0, 0)
        self.assertTrue(node['player'] == -1 and node['has_city'] is False)
        board.build_town(0, 0)
        self.assertTrue(node['player'] == 0 and node['has_city'] is False)
        board.build_city(0, 0)
        self.assertTrue(node['player'] == 0 and node['has_city'] is True)
        finishing_node = board.nodes[8]
        node['roads'].append({'player_id': 2, 'node_id': 8})
        finishing_node['roads'].append({'player_id': 2, 'node_id': 0})
        board.build_town(2, 0)
        self.assertTrue(node['player'] != 2)
        board.build_city(2, 0)
        self.assertTrue(node['player'] != 2)
        node = board.nodes[1]
        board.build_town(0, 1)
        self.assertTrue(node['player'] == -1 and node['has_city'] is False)
        node = board.nodes[1]
        board.build_city(0, 1)
        self.assertTrue(node['player'] == -1 and node['has_city'] is False)
        board.nodes[1]['roads'].append({'player_id': 0, 'node_id': 2})
        board.nodes[2]['roads'].append({'player_id': 0, 'node_id': 1})
        node = board.nodes[2]
        board.build_town(0, 2)
        board.build_city(0, 2)
        self.assertTrue(node['player'] == 0 and node['has_city'] is True)

    def test_build_road(self):
        board = Board()
        node = board.nodes[0]
        self.assertTrue(len(node['roads']) == 0 and node['player'] == -1 and node['has_city'] is False)
        node['player'] = 0
        finishing_node = board.nodes[1]
        board.build_road(0, 0, 1)
        board.build_city(0, 0)
        finishing_node = board.nodes[8]
        board.build_road(0, 0, 8)
        node = board.nodes[1]
        finishing_node = board.nodes[2]
        board.build_road(0, 1, 2)
        board.nodes[8]['player'] = 2
        node = board.nodes[8]
        finishing_node = board.nodes[0]
        board.build_road(2, 8, 0)
        node = board.nodes[8]
        finishing_node = board.nodes[9]
        board.build_road(0, 8, 9)
        board.build_city(2, 8)
        node = board.nodes[8]
        finishing_node = board.nodes[9]
        board.build_road(0, 8, 9)
        board.build_road(2, 8, 9)
        node = board.nodes[9]
        finishing_node = board.nodes[10]
        board.build_road(0, 8, 9)
        # Intento de construir una carretera inválida (ya existe una carretera de otro jugador en el nodo de destino)
        board.nodes[2]['roads'].append({'player_id': 1, 'node_id': 3})
        node = board.nodes[2]
        finishing_node = board.nodes[3]
        board.build_road(0, 2, 3)
        # Tras intentar construir una carretera inválida, comprobamos que el estado no cambia
        board.build_road(2, 8, 0)
        node = board.nodes[8]
        finishing_node = board.nodes[9]
        board.build_road(0, 8, 9)
        board.build_city(2, 8)
        node = board.nodes[8]
        finishing_node = board.nodes[9]
        board.build_road(0, 8, 9)
        board.build_road(2, 8, 9)
        node = board.nodes[9]
        finishing_node = board.nodes[10]
        board.build_road(0, 8, 9)

    def test_move_thief(self):
        board = Board()
        terrain = board.terrain
        self.assertTrue(terrain[7]['has_thief'])
        response = board.move_thief(5)
        self.assertTrue(terrain[5]['has_thief'] and not terrain[7]['has_thief'] and response['response'])
        response = board.move_thief(3)
        self.assertTrue(terrain[3]['has_thief'] and not terrain[5]['has_thief'] and not terrain[7]['has_thief'] and response['response'])
        response = board.move_thief(3)
        self.assertTrue(terrain[response['terrain_id']]['has_thief'] and not terrain[3]['has_thief'] and not response['response'])

    def test_valid_town_nodes(self):
        board = Board()
        board.nodes[0]['roads'].append({'player_id': 0, 'node_id': 1})
        board.nodes[1]['roads'].append({'player_id': 0, 'node_id': 0})
        board.nodes[1]['roads'].append({'player_id': 0, 'node_id': 2})
        board.nodes[2]['roads'].append({'player_id': 0, 'node_id': 1})
        valid_nodes = board.valid_town_nodes(0)
        self.assertEqual(valid_nodes, [0, 1, 2])
        board.nodes[2]['player'] = 1
        valid_nodes = board.valid_town_nodes(0)
        self.assertEqual(valid_nodes, [0])
        board.nodes[2]['player'] = -1
        board.nodes[1]['player'] = 1
        valid_nodes = board.valid_town_nodes(0)
        self.assertEqual(valid_nodes, [])
        valid_nodes_j1 = board.valid_town_nodes(1)
        valid_nodes_j2 = board.valid_town_nodes(2)
        valid_nodes_j3 = board.valid_town_nodes(3)
        self.assertEqual(valid_nodes_j1, [])
        self.assertEqual(valid_nodes_j2, [])
        self.assertEqual(valid_nodes_j3, [])

    def test_valid_city_nodes(self):
        board = Board()
        board.nodes[0]['player'] = 0
        board.nodes[53]['player'] = 0
        board.nodes[4]['player'] = 1
        valid_nodes = board.valid_city_nodes(0)
        self.assertEqual(valid_nodes, [0, 53])
        board.build_city(0, 53)
        valid_nodes = board.valid_city_nodes(0)
        self.assertEqual(valid_nodes, [0])
        valid_nodes = board.valid_city_nodes(1)
        self.assertEqual(valid_nodes, [4])

    def test_valid_road_nodes(self):
        board = Board()
        board.nodes[0]['player'] = 0
        board.nodes[0]['roads'].append({'player_id': 0, 'node_id': 1})
        board.nodes[1]['roads'].append({'player_id': 0, 'node_id': 0})
        valid_roads = board.valid_road_nodes(0)
        self.assertEqual(valid_roads, [{'starting_node': 1, 'finishing_node': 2}, {'starting_node': 0, 'finishing_node': 8}])
        board.nodes[1]['roads'].append({'player_id': 0, 'node_id': 2})
        board.nodes[2]['roads'].append({'player_id': 0, 'node_id': 1})
        valid_roads = board.valid_road_nodes(0)
        self.assertEqual(valid_roads, [{'starting_node': 2, 'finishing_node': 3}, {'starting_node': 0, 'finishing_node': 8},
                               {'starting_node': 2, 'finishing_node': 10}])
        board.nodes[2]['player'] = 1
        valid_roads = board.valid_road_nodes(0)
        self.assertEqual(valid_roads, [{'starting_node': 0, 'finishing_node': 8}])
        board.nodes[2]['player'] = -1
        board.nodes[3]['player'] = 1
        valid_roads = board.valid_road_nodes(0)
        self.assertEqual(valid_roads, [{'starting_node': 2, 'finishing_node': 3}, {'starting_node': 0, 'finishing_node': 8},
                               {'starting_node': 2, 'finishing_node': 10}])
        board.nodes[2]['roads'].append({'player_id': 0, 'node_id': 3})
        board.nodes[3]['roads'].append({'player_id': 0, 'node_id': 2})
        valid_roads = board.valid_road_nodes(0)
        self.assertEqual(valid_roads, [{'starting_node': 0, 'finishing_node': 8}, {'starting_node': 2, 'finishing_node': 10}])
        board.nodes[3]['roads'].append({'player_id': 0, 'node_id': 4})
        board.nodes[4]['roads'].append({'player_id': 0, 'node_id': 3})
        valid_roads = board.valid_road_nodes(0)
        self.assertEqual(valid_roads, [{'starting_node': 4, 'finishing_node': 5}, {'starting_node': 0, 'finishing_node': 8},
                               {'starting_node': 2, 'finishing_node': 10}, {'starting_node': 4, 'finishing_node': 12}])

    def test_valid_starting_nodes(self):
        board = Board()
        valid_nodes = board.valid_starting_nodes()
        self.assertEqual(valid_nodes, [9, 10, 11, 12, 13, 18, 19, 20, 21, 22, 23, 24, 29, 30, 31, 32, 33, 34, 35, 40, 41, 42,
                               43, 44])
        board.nodes[11]['player'] = 0
        valid_nodes = board.valid_starting_nodes()
        self.assertEqual(valid_nodes, [9, 13, 18, 19, 20, 22, 23, 24, 29, 30, 31, 32, 33, 34, 35, 40, 41, 42, 43, 44])

    def test_check_for_player_harbors(self):
        board = Board()
        board.nodes[3]['player'] = 0
        board.nodes[7]['player'] = 0
        board.nodes[28]['player'] = 1
        harbor_response = board.check_for_player_harbors(0, MaterialConstants.CEREAL)
        self.assertEqual(harbor_response, HarborConstants.CEREAL)
        harbor_response = board.check_for_player_harbors(1, MaterialConstants.CEREAL)
        self.assertEqual(harbor_response, HarborConstants.NONE)
        harbor_response = board.check_for_player_harbors(1, MaterialConstants.MINERAL)
        self.assertEqual(harbor_response, HarborConstants.MINERAL)
        harbor_response = board.check_for_player_harbors(0, MaterialConstants.MINERAL)
        self.assertEqual(harbor_response, HarborConstants.ALL)


if __name__ == '__main__':
    unittest.main()
