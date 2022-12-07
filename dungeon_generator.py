import sys 

sys.path.insert(1, 'core')
import core
import random as rand

# TODO: implement rank system to make it computational faster
# TODO: move this to separate file
class Disjoin_set_2d():
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.data = []
        for row in range(height):
            self.data.append([])
            for col in range(width):
                self.data[-1].append([row, col])

    def find(self, row: int, col: int) :
        parent = self.data[row][col]
        if parent == [row, col]:
            return [row, col]
        root = self.find(parent[0], parent[1])
        self.data[row][col] = root
        return root

    def merge(self, p1, p2):
        p1 = self.find(p1[0], p1[1])
        p2 = self.find(p2[0], p2[1])

        if p1 == p2:
            return
        self.data[p1[0]][p1[1]] = p2
class Dungeon_generator_additive():
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def generate(self):
        adj_matrix_vertical = []
        for _ in range(self.height - 1):
            adj_matrix_vertical.append([])
            for _ in range(self.width - 1):
                adj_matrix_vertical[-1].append(False)

        adj_matrix_horizontal = []
        for _ in range(self.height - 1):
            adj_matrix_horizontal.append([])
            for _ in range(self.width - 1):
                adj_matrix_horizontal[-1].append(False)

        start = rand.randint(0, self.width - 2)
        end = rand.randint(0, self.height - 2)

        set = Disjoin_set_2d(self.width, self.height)
        while (set.find(start, 0) != set.find(end, self.width - 1)):
            rand_row = rand.randint(0, self.height - 2)
            rand_col = rand.randint(0, self.width - 2)
            is_hor = rand.randint(0, 1)
            if is_hor: 
                set.merge([rand_row, rand_col], [rand_row, rand_col + 1])
                adj_matrix_horizontal[rand_row][rand_col] = True
            else:
                set.merge([rand_row, rand_col], [rand_row + 1, rand_col])
                adj_matrix_vertical[rand_row][rand_col] = True
            
class Dungeon_generator_subtractive():
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def generate(self):
        adj_matrix_vertical = []
        for _ in range(self.height - 1):
            adj_matrix_vertical.append([])
            for _ in range(self.width - 1):
                adj_matrix_vertical[-1].append(False)

        adj_matrix_horizontal = []
        for _ in range(self.height - 1):
            adj_matrix_horizontal.append([])
            for _ in range(self.width - 1):
                adj_matrix_horizontal[-1].append(False)

        start = rand.randint(0, self.width - 2)
        end = rand.randint(0, self.height - 2)

        set = Disjoin_set_2d(self.width, self.height)
        while (set.find(start, 0) != set.find(end, self.width - 1)):
            rand_row = rand.randint(0, self.height - 2)
            rand_col = rand.randint(0, self.width - 2)
            is_hor = rand.randint(0, 1)
            if is_hor: 
                set.merge([rand_row, rand_col], [rand_row, rand_col + 1])
                adj_matrix_horizontal[rand_row][rand_col] = True
            else:
                set.merge([rand_row, rand_col], [rand_row + 1, rand_col])
                adj_matrix_vertical[rand_row][rand_col] = True