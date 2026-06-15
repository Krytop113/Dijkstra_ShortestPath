import heapq

def dijkstra(graph, src):
    """
    Menghitung jarak terpendek dari simpul asal 'src' ke semua simpul lain
    menggunakan algoritma Dijkstra dengan min-heap (heapq) untuk optimasi O(E log V).
    """
    num_nodes = len(graph)
    INF = 10**9
    dist = [INF] * num_nodes
    prev = [-1] * num_nodes
    dist[src] = 0
    
    # Priority queue menyimpan pasangan (jarak, simpul)
    pq = [(0, src)]
    
    while pq:
        d, u = heapq.heappop(pq)
        
        if d > dist[u]:
            continue
            
        for v in range(num_nodes):
            weight = graph[u][v]
            if weight > 0:
                new_dist = dist[u] + weight
                if new_dist < dist[v]:
                    dist[v] = new_dist
                    prev[v] = u
                    heapq.heappush(pq, (new_dist, v))
                    
    return dist, prev


def dijkstra_with_steps(graph, src):
    """
    Menjalankan algoritma Dijkstra dan mencatat snapshot status (jarak, prev, visited)
    di setiap iterasi untuk analisis langkah-demi-langkah (tracing).
    """
    num_nodes = len(graph)
    INF = 10**9
    dist = [INF] * num_nodes
    prev = [-1] * num_nodes
    visited = [False] * num_nodes
    dist[src] = 0
    
    steps = []
    
    # Langkah inisialisasi (Langkah 0)
    steps.append({
        "step": 0,
        "selected_node": None,
        "dist": list(dist),
        "prev": list(prev),
        "visited": [i for i, v in enumerate(visited) if v],
        "message": f"Inisialisasi: Jarak ke simpul asal {src} diatur ke 0, simpul lainnya ke tak hingga (INF)."
    })
    
    for step_num in range(1, num_nodes + 1):
        u = -1
        # Cari simpul belum dikunjungi dengan jarak terkecil
        for i in range(num_nodes):
            if not visited[i] and (u == -1 or dist[i] < dist[u]):
                u = i
                
        if u == -1 or dist[u] == INF:
            steps.append({
                "step": step_num,
                "selected_node": None,
                "dist": list(dist),
                "prev": list(prev),
                "visited": [i for i, v in enumerate(visited) if v],
                "message": "Tidak ada simpul terjangkau yang tersisa. Proses selesai."
            })
            break
            
        visited[u] = True
        relaxed_nodes = []
        
        # Relaksasi tetangga simpul u
        for v in range(num_nodes):
            weight = graph[u][v]
            if weight > 0 and not visited[v]:
                new_dist = dist[u] + weight
                if new_dist < dist[v]:
                    old_dist = dist[v]
                    dist[v] = new_dist
                    prev[v] = u
                    relaxed_nodes.append(f"Simpul {v} ({'INF' if old_dist == INF else old_dist} -> {new_dist})")
                    
        relaxation_msg = "Relaksasi tetangga: " + (", ".join(relaxed_nodes) if relaxed_nodes else "Tidak ada perubahan jarak tetangga.")
        steps.append({
            "step": step_num,
            "selected_node": u,
            "dist": list(dist),
            "prev": list(prev),
            "visited": [i for i, v in enumerate(visited) if v],
            "message": f"Simpul {u} terpilih (jarak terkecil: {dist[u]}). {relaxation_msg}"
        })
        
    return dist, prev, steps


def reconstruct_path(prev, src, dst):
    """
    Merekonstruksi lintasan terpendek dari array 'prev' hasil Dijkstra.
    """
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


def check_graph_connectivity(graph, start_node=0):
    """
    Memeriksa konektivitas graf dari simpul tertentu (biasanya depot)
    menggunakan algoritma Breadth-First Search (BFS).
    """
    num_nodes = len(graph)
    if num_nodes == 0:
        return {"is_connected": True, "unreachable_nodes": [], "connected_nodes": []}
        
    visited = [False] * num_nodes
    queue = [start_node]
    visited[start_node] = True
    head = 0
    
    while head < len(queue):
        u = queue[head]
        head += 1
        for v in range(num_nodes):
            if graph[u][v] > 0 and not visited[v]:
                visited[v] = True
                queue.append(v)
                
    unreachable = [i for i in range(num_nodes) if not visited[i]]
    return {
        "is_connected": len(unreachable) == 0,
        "unreachable_nodes": unreachable,
        "connected_nodes": [i for i in range(num_nodes) if visited[i]]
    }