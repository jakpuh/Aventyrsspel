import networkx as nx

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def read_graph():
    graph_adjacency_list = { }
    for line in open("utils/input.txt"):
        line = list(map(int, line.rstrip("\t\r\n").split(" ")))
        graph_adjacency_list.update({ line[0]: { e: 1 for e in line[1:] } })
    return graph_adjacency_list

graph_data = read_graph()
G = nx.Graph(graph_data)
nx.draw_networkx(G, with_labels = True, node_color = "c", edge_color = "k", font_size = 8)

plt.axis('off')
plt.draw()
plt.savefig("graph.pdf")
