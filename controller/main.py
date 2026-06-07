from controller.dijkstra import dijkstra, reconstruct_path

VEHICLE_CAPACITY = 100


def get_dijkstra_overview(graph, packages, depot_node):
    if not graph:
        return {
            "depot_paths": [],
            "package_paths": [],
            "vehicle_log": [],
            "stats": {},
        }

    num_nodes = len(graph)

    depot_dist, depot_prev = dijkstra(graph, depot_node)
    depot_paths = []
    for node in range(num_nodes):
        path = reconstruct_path(depot_prev, depot_node, node)
        distance = depot_dist[node] if depot_dist[node] < 10**9 else None
        depot_paths.append(
            {
                "node": node,
                "path": path,
                "distance": distance,
                "reachable": path is not None,
            }
        )

    sorted_packages = sorted(
        packages, key=lambda x: (x["priority"], x["deadline"], x["volume"])
    )

    loaded_packages = []
    package_results = {}
    current_load = 0

    for pkg in sorted_packages:
        pkg_id = pkg["id"]
        if current_load + pkg["volume"] <= VEHICLE_CAPACITY:
            loaded_packages.append(pkg)
            current_load += pkg["volume"]
            package_results[pkg_id] = {
                "package": pkg,
                "status": "Loaded",
                "details": "Dimuat ke kendaraan.",
                "arrival_time": None,
                "path": None,
            }
        else:
            package_results[pkg_id] = {
                "package": pkg,
                "status": "Failed_Capacity",
                "details": "Gagal Terkirim (Kapasitas Kendaraan Penuh)",
                "arrival_time": None,
                "path": None,
            }

    current_node = depot_node
    current_time = 0
    vehicle_log = [f"Kendaraan berangkat dari Depot (Node {depot_node}) pada waktu 0. Total muatan: {current_load}/{VEHICLE_CAPACITY}"]
    
    undelivered = list(loaded_packages)
    dijkstra_cache = {}

    while undelivered:
        dests = list(set(pkg["dst"] for pkg in undelivered))
        
        if current_node not in dijkstra_cache:
            dijkstra_cache[current_node] = dijkstra(graph, current_node)
        
        dist, prev = dijkstra_cache[current_node]
        
        nearest_dst = None
        min_dist = float("inf")
        
        for d in dests:
            if dist[d] < 10**9 and dist[d] < min_dist:
                min_dist = dist[d]
                nearest_dst = d
                
        if nearest_dst is None:
            for pkg in undelivered:
                package_results[pkg["id"]]["status"] = "Failed_Unreachable"
                package_results[pkg["id"]]["details"] = "Gagal Terkirim (Tujuan tidak terhubung)"
            vehicle_log.append("Kendaraan berhenti. Sisa tujuan pengiriman tidak dapat dijangkau dari posisi saat ini.")
            break
            
        path = reconstruct_path(prev, current_node, nearest_dst)
        current_time += min_dist
        
        path_str = " -> ".join(map(str, path))
        vehicle_log.append(
            f"Kendaraan bergerak dari Node {current_node} ke Node {nearest_dst} melalui jalur [{path_str}] (Jarak: {min_dist}). Waktu kumulatif: {current_time}."
        )
        
        current_node = nearest_dst
        
        delivered_here = [pkg for pkg in undelivered if pkg["dst"] == current_node]
        for pkg in delivered_here:
            pkg_id = pkg["id"]
            package_results[pkg_id]["path"] = path
            package_results[pkg_id]["arrival_time"] = current_time
            
            if current_time <= pkg["deadline"]:
                package_results[pkg_id]["status"] = "Success"
                package_results[pkg_id]["details"] = f"Berhasil Terkirim (Waktu tiba: {current_time}, Deadline: H{pkg['deadline']})"
                vehicle_log.append(
                    f" - Paket #{pkg_id} berhasil terkirim ke Node {current_node} tepat waktu (Tiba: {current_time}, Deadline: H{pkg['deadline']})."
                )
            else:
                package_results[pkg_id]["status"] = "Failed_Deadline"
                package_results[pkg_id]["details"] = f"Gagal Terkirim (Terlambat: Waktu tiba {current_time}, Deadline: H{pkg['deadline']})"
                vehicle_log.append(
                    f" - Paket #{pkg_id} GAGAL terkirim ke Node {current_node} karena terlambat (Tiba: {current_time}, Deadline: H{pkg['deadline']})."
                )
                
            undelivered.remove(pkg)

    final_package_paths = []
    success_count = 0
    failed_count = 0
    
    for pkg in packages:
        res = package_results[pkg["id"]]
        final_package_paths.append(res)
        if res["status"] == "Success":
            success_count += 1
        else:
            failed_count += 1

    stats = {
        "success_count": success_count,
        "failed_count": failed_count,
        "total_load": current_load,
        "capacity": VEHICLE_CAPACITY,
    }

    return {
        "depot_paths": depot_paths,
        "package_paths": final_package_paths,
        "vehicle_log": vehicle_log,
        "stats": stats,
    }
