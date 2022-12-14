from dungeon_generator_algorithm import *
from room import Room
from scene import Scene

class Dungeon_generator():
    def __init__(self, layout_generator: Layout_generator):
        self.structure_algorithm = layout_generator

    def generate(self):
        adj_layout = self.layout_generator.generate(3, 3)
        adj_rooms = []
        for _ in len(adj_layout):
            adj_rooms.append([])
        for node in adj_layout:
            room = Room()
            for neighbour in node:
                if neighbour[1] == 'R':
                    room.neighbours['R'] = neighbour[0]
                elif neighbour[1] == 'L':
                    room.neighbours['L'] = neighbour[0]
                elif neighbour[1] == 'U':
                    room.neighbours['U'] = neighbour[0]
                elif neighbour[1] == 'D':
                    room.neighbours['D'] = neighbour[0]
            room.scene = Scene(room.neighbours.keys())
            adj_rooms.append(room)
        return adj_rooms

