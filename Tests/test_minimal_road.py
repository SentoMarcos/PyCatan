import unittest
from Classes.Board import Board

class MinimalRoadTest(unittest.TestCase):
    def test_road_conflict(self):
        board = Board()
        board.nodes[0]['player'] = 0
        board.build_road(0, 0, 1)
        board.build_city(0, 0)
        board.build_road(0, 0, 8)
        board.build_road(0, 1, 2)
        board.nodes[8]['player'] = 2
        # Estado antes
        self.assertEqual(board.nodes[8]['roads'], [{'player_id': 0, 'node_id': 0}])
        self.assertEqual(board.nodes[0]['roads'], [{'player_id': 0, 'node_id': 1}, {'player_id': 0, 'node_id': 8}])
        # Intento conflictivo
        board.build_road(2, 8, 0)
        # Estado después: debe ser igual
        self.assertEqual(board.nodes[8]['roads'], [{'player_id': 0, 'node_id': 0}])
        self.assertEqual(board.nodes[0]['roads'], [{'player_id': 0, 'node_id': 1}, {'player_id': 0, 'node_id': 8}])

if __name__ == '__main__':
    unittest.main()
