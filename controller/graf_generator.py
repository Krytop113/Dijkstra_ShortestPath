import random

def generate_random_graph(num_nodes):
    graph = [[0 for _ in range(num_nodes)] for _ in range(num_nodes)]
    visited = [0]
    unvisited = list(range(1, num_nodes))

    while unvisited:
        node_index = random.randrange(len(unvisited))
        u = unvisited.pop(node_index)
        v = random.choice(visited)
        weight = random.randint(5, 44)

        graph[u][v] = weight
        graph[v][u] = weight
        visited.append(u)

    for i in range(num_nodes):
        for j in range(i + 1, num_nodes):
            if graph[i][j] == 0 and random.random() < 0.25:
                weight = random.randint(5, 54)
                graph[i][j] = weight
                graph[j][i] = weight

    return graph

