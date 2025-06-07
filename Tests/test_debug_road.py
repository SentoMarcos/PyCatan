import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from Classes.Board import Board

class DebugTest(unittest.TestCase):
    pass
    # def test_debug_road(self):
    #     board = Board()
    #     node = board.nodes[0]
    #     node['player'] = 0
    #     finishing_node = board.nodes[1]
    #     board.build_road(0, 0, 1)
    #     board.build_city(0, 0)
    #     finishing_node = board.nodes[8]
    #     board.build_road(0, 0, 8)
    #     node = board.nodes[1]
    #     finishing_node = board.nodes[2]
    #     board.build_road(0, 1, 2)
    #     board.nodes[8]['player'] = 2
    #     node = board.nodes[8]
    #     finishing_node = board.nodes[0]
    #     board.build_road(2, 8, 0)
    #     print('node[8][roads]:', node['roads'])
    #     print('node[0][roads]:', finishing_node['roads'])
    #     for i, n in enumerate(board.nodes):
    #         print(f'node[{i}]:', n['roads'], n['player'])
    #     import sys; sys.exit()
    #     self.assertTrue(node['roads'] == [{'player_id': 0, 'node_id': 0}])
    #     self.assertTrue(finishing_node['roads'] == [{'player_id': 0, 'node_id': 1}, {'player_id': 0, 'node_id': 8}])
