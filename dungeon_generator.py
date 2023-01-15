from dungeon_generator_algorithm import *
from room import Room
import scene

class Dungeon_generator():
    def __init__(self, layout_generator: Layout_generator):
        self.layout_generator = layout_generator

    def _find_longest_path(self, adj, node, seen) -> tuple[2]: 
        if node in seen:
            return [-1, -1]
        seen.add(node)
        max = 0
        max_node = node
        for child in adj[node]:
            res = self._find_longest_path(adj, child[0], seen)
            if res[0] > max:
                max = res[0]
                max_node = res[1]
        return (max + 1, max_node)

    def generate(self, screen, left_sidebar, right_sidebar) -> list[Room]:
        adj_layout = self.layout_generator.generate(3, 3)
        adj_rooms = []
        [_, boss_room] = self._find_longest_path(adj_layout, 0, set())
        for i,node in enumerate(adj_layout):
            room = Room()
            for neighbour in node:
                if neighbour[1] in 'RLUD':
                    room.neighbours[neighbour[1]] = neighbour[0]
                else:
                    raise Exception("Invalid neighbour direction")
            if i == 0:
                room.scene = scene.Empty_scene(room.neighbours.keys(), screen, left_sidebar, right_sidebar)
            elif i == boss_room:
                INVERTED_SIDES = {
                    'R': 'L',
                    'L': 'R',
                    'U': 'D',
                    'D': 'U'
                }
                exit_side = INVERTED_SIDES[list(room.neighbours.keys())[0]] 
                room.scene = scene.Boss_scene(room.neighbours.keys(), exit_side, screen, left_sidebar, right_sidebar)
            else:
                room.scene = scene.Challenge_scene(room.neighbours.keys(), screen, left_sidebar, right_sidebar)
            adj_rooms.append(room)

        return adj_rooms

