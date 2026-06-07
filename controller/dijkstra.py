def dijkstra(graph, src):
    num_nodes = len(graph)
    INF = 10**9
    dist = [INF] * num_nodes
    prev = [-1] * num_nodes
    visited = [False] * num_nodes
    dist[src] = 0

    for _ in range(num_nodes):
        u = -1
        for i in range(num_nodes):
            if not visited[i] and (u == -1 or dist[i] < dist[u]):
                u = i
        if u == -1 or dist[u] == INF:
            break
        visited[u] = True

        for v in range(num_nodes):
            if graph[u][v] > 0 and dist[u] + graph[u][v] < dist[v]:
                dist[v] = dist[u] + graph[u][v]
                prev[v] = u

    return dist, prev


def reconstruct_path(prev, src, dst):
    path = []
    cur = dst
    while cur != -1 and cur != src:
        path.insert(0, cur)
        cur = prev[cur]
    if cur == src:
        path.insert(0, src)
    else:
        return None
    return path