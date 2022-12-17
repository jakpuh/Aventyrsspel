from dungeon_generator_algorithm import *
from room import Room
from scene import Scene

class Dungeon_generator():
    def __init__(self, layout_generator: Layout_generator):
        self.layout_generator = layout_generator

    def generate(self, screen, hotbar) -> list[Room]:
    #def generate(self):
        adj_layout = self.layout_generator.generate(3, 3)
        adj_rooms = []
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
                else:
                    raise Exception("Invalid neighbour direction")
            room.scene = Scene(room.neighbours.keys(), screen, hotbar)
            adj_rooms.append(room)
        return adj_rooms

