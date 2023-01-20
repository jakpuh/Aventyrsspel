import sys 

sys.path.insert(1, 'core')
import core
import random as rand


# TODO: implement rank system to make it computational faster
# TODO: move this to separate file
class Disjoin_set_2d():
    def __init__(self, width: int, height: int):
        width = width
        height = height
        self.data = []
        for row in range(height):
            self.data.append([])
            for col in range(width):
                self.data[-1].append([row, col])

    def find(self, p) :
        row = p[0]
        col = p[1]
        parent = self.data[row][col]
        if parent == [row, col]:
            return [row, col]
        root = self.find(parent)
        self.data[row][col] = root
        return root

    def merge(self, p1, p2):
        p1 = self.find(p1)
        p2 = self.find(p2)

        if p1 == p2:
            return
        self.data[p1[0]][p1[1]] = p2

class Layout_generator():
    def generate(self, width, height):
        pass

# Dont use. Generates to many paths
# Also doesn't work
class Layout_generator_additive(Layout_generator):
    def generate(self, width, height):
        adj_matrix_vertical = []
        for _ in range(height - 1):
            adj_matrix_vertical.append([])
            for _ in range(width - 1):
                adj_matrix_vertical[-1].append(False)

        adj_matrix_horizontal = []
        for _ in range(height - 1):
            adj_matrix_horizontal.append([])
            for _ in range(width - 1):
                adj_matrix_horizontal[-1].append(False)

        start = rand.randint(0, width - 2)
        end = rand.randint(0, height - 2)

        # Doesn't work. Rand could select the same edge multiple times
        set = Disjoin_set_2d(width, height)
        while (set.find((start, 0)) != set.find((end, width - 1))):
            rand_row = rand.randint(0, height - 2)
            rand_col = rand.randint(0, width - 2)
            is_hor = rand.randint(0, 1)
            if is_hor: 
                set.merge([rand_row, rand_col], [rand_row, rand_col + 1])
                adj_matrix_horizontal[rand_row][rand_col] = True
            else:
                set.merge([rand_row, rand_col], [rand_row + 1, rand_col])
                adj_matrix_vertical[rand_row][rand_col] = True

            
class Layout_generator_spanning(Layout_generator):
    def generate(self, width, height):
        adj_matrix_vertical = []
        for _ in range(height - 1):
            adj_matrix_vertical.append([])
            for _ in range(width - 1):
                adj_matrix_vertical[-1].append(False)

        adj_matrix_horizontal = []
        for _ in range(height - 1):
            adj_matrix_horizontal.append([])
            for _ in range(width - 1):
                adj_matrix_horizontal[-1].append(False)

        # start = rand.randint(0, width - 2)
        # end = rand.randint(0, height - 2)

        edges = []
        for row in range(0, height - 1):
            for col in range(0, width - 1):
                edges.append(((row, col), (row + 1, col), 'D'))
                edges.append(((row, col), (row, col + 1), 'R'))
        rand.shuffle(edges)

        selected_edges = []

        # using variant of kruskal's algorithm to generate a spanning tree
        set = Disjoin_set_2d(width, height)
        for edge in edges:
            if set.find(edge[0]) == set.find(edge[1]):
                continue
            set.merge(edge[0], edge[1])
            selected_edges.append(edge)

        adj = []
        for _ in range(width * height - 1):
            adj.append([])  
        for edge in selected_edges:
            adj[edge[0][0] * width + edge[0][1]].append((edge[1][0] * width + edge[1][1], edge[2]))
            adj[edge[1][0] * width + edge[1][1]].append((edge[0][0] * width + edge[0][1], 'L' if edge[2] == 'R' else 'U'))

        return adj
