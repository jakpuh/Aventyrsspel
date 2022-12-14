from dungeon_generator_algorithm import *
from room import Room
from scene import Challenge_scene

class Dungeon_generator():
    def __init__(self, layout_generator: Layout_generator):
        self.layout_generator = layout_generator

    def generate(self, screen, left_sidebar, right_sidebar) -> list[Room]:
    #def generate(self):
        adj_layout = self.layout_generator.generate(3, 3)
        adj_rooms = []
        for node in adj_layout:
            room = Room()
            for neighbour in node:
                if neighbour[1] in 'RLUD':
                    room.neighbours[neighbour[1]] = neighbour[0]
                else:
                    raise Exception("Invalid neighbour direction")
            room.scene = Challenge_scene(room.neighbours.keys(), screen, left_sidebar, right_sidebar)
            adj_rooms.append(room)
        return adj_rooms

