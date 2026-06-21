from controller.dijkstra import dijkstra, reconstruct_path, check_graph_connectivity

def get_dijkstra_overview(graph, packages, depot_node, vehicle_capacity):
    if not graph:
        return {
            "depot_paths": [],
            "package_paths": [],
            "vehicle_log": [],
            "stats": {},
            "connectivity": {},
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

    connectivity = check_graph_connectivity(graph, depot_node)

    package_states = {}
    for pkg in packages:
        pkg_id = pkg["id"]
        if pkg["volume"] > vehicle_capacity:
            package_states[pkg_id] = {
                "package": pkg,
                "status": "Failed_Capacity",
                "details": f"Gagal Terkirim (Volume paket {pkg['volume']} melebihi kapasitas kendaraan {vehicle_capacity})",
                "arrival_time": None,
                "path": None,
            }
        elif depot_dist[pkg["src"]] >= 10**9:
            package_states[pkg_id] = {
                "package": pkg,
                "status": "Failed_Unreachable",
                "details": f"Gagal Terkirim (Asal paket simpul {pkg['src']} tidak dapat dijangkau dari Depot)",
                "arrival_time": None,
                "path": None,
            }
        else:
            src_dist, _ = dijkstra(graph, pkg["src"])
            if src_dist[pkg["dst"]] >= 10**9:
                package_states[pkg_id] = {
                    "package": pkg,
                    "status": "Failed_Unreachable",
                    "details": f"Gagal Terkirim (Tujuan paket simpul {pkg['dst']} tidak dapat dijangkau dari Asal {pkg['src']})",
                    "arrival_time": None,
                    "path": None,
                }
            else:
                package_states[pkg_id] = {
                    "package": pkg,
                    "status": "Undelivered",
                    "details": "Menunggu penjemputan.",
                    "arrival_time": None,
                    "path": [],
                }

    current_node = depot_node
    current_time = 0
    current_load = 0
    
    trip_number = 1
    vehicle_log = [
        f"Trip #{trip_number} dimulai: Kendaraan berangkat dari Depot (Node {depot_node}) pada waktu 0. Muatan: 0/{vehicle_capacity}"
    ]

    while True:
        candidates = []
        
        for pkg_id, state in package_states.items():
            pkg = state["package"]
            if state["status"] == "Undelivered":
                if current_load + pkg["volume"] <= vehicle_capacity:
                    candidates.append((pkg["src"], "pickup"))
            elif state["status"] == "PickedUp":
                candidates.append((pkg["dst"], "delivery"))

        has_undelivered = any(s["status"] == "Undelivered" for s in package_states.values())
        if not candidates:
            if current_node != depot_node:
                candidates.append((depot_node, "return_to_depot"))
            else:
                break

        dist, prev = dijkstra(graph, current_node)

        best_candidate = None
        best_score = -float("inf")
        best_path = None
        best_dist = None

        for target_node, action in candidates:
            d_to_target = dist[target_node]
            if d_to_target >= 10**9:
                continue
                
            score = -d_to_target
            
            if action == "pickup":
                pkgs_here = [
                    s["package"] for s in package_states.values()
                    if s["status"] == "Undelivered" and s["package"]["src"] == target_node and current_load + s["package"]["volume"] <= vehicle_capacity
                ]
                for p in pkgs_here:
                    score += (4 - p["priority"]) * 30
                    eta = current_time + d_to_target
                    if eta <= p["deadline"]:
                        score += max(0, 100 - (p["deadline"] - eta) * 5)
                    else:
                        score -= 50
                        
            elif action == "delivery":
                score += 100
                pkgs_here = [
                    s["package"] for s in package_states.values()
                    if s["status"] == "PickedUp" and s["package"]["dst"] == target_node
                ]
                for p in pkgs_here:
                    score += (4 - p["priority"]) * 45
                    eta = current_time + d_to_target
                    if eta <= p["deadline"]:
                        score += max(0, 150 - (p["deadline"] - eta) * 10)
                    else:
                        score -= 100
                        
            elif action == "return_to_depot":
                score -= 40
                if current_load > 0:
                    score -= 500

            if score > best_score:
                best_score = score
                best_candidate = (target_node, action)
                best_dist = d_to_target
                best_path = reconstruct_path(prev, current_node, target_node)

        if best_candidate is None:
            for pkg_id, state in package_states.items():
                if state["status"] in ["Undelivered", "PickedUp"]:
                    state["status"] = "Failed_Unreachable"
                    state["details"] = "Gagal Terkirim (Tujuan/Asal terisolasi dari rute kendaraan)"
            vehicle_log.append(
                f"Kendaraan berhenti di Node {current_node}. Sisa paket tidak dapat dijangkau dari posisi saat ini."
            )
            break

        target_node, action = best_candidate
        
        current_time += best_dist
        path_str = " -> ".join(map(str, best_path))
        
        for state in package_states.values():
            if state["status"] == "PickedUp":
                state["path"].extend(best_path[1:])

        if action == "return_to_depot":
            vehicle_log.append(
                f"Kendaraan kembali ke Depot (Node {target_node}) melalui jalur [{path_str}] (Jarak: {best_dist}). Waktu kumulatif: {current_time}."
            )
            current_node = target_node
        else:
            vehicle_log.append(
                f"Kendaraan bergerak dari Node {current_node} ke Node {target_node} melalui jalur [{path_str}] (Jarak: {best_dist}). Waktu kumulatif: {current_time}."
            )
            current_node = target_node

        # Perform deliveries at the current node (frees up capacity)
        delivered_here = [
            pkg_id for pkg_id, s in package_states.items()
            if s["status"] == "PickedUp" and s["package"]["dst"] == current_node
        ]
        for pkg_id in delivered_here:
            state = package_states[pkg_id]
            pkg = state["package"]
            current_load -= pkg["volume"]
            state["arrival_time"] = current_time
            
            if current_time <= pkg["deadline"]:
                state["status"] = "Success"
                state["details"] = f"Berhasil Terkirim (Tiba: {current_time}, Deadline: H{pkg['deadline']})"
                vehicle_log.append(
                    f" - Paket #{pkg_id} berhasil terkirim ke Node {current_node} tepat waktu (Tiba: {current_time}, Deadline: H{pkg['deadline']}). Muatan kendaraan: {current_load}/{vehicle_capacity}"
                )
            else:
                state["status"] = "Failed_Deadline"
                state["details"] = f"Gagal Terkirim (Terlambat: Waktu tiba {current_time}, Deadline: H{pkg['deadline']})"
                vehicle_log.append(
                    f" - Paket #{pkg_id} GAGAL terkirim ke Node {current_node} karena terlambat (Tiba: {current_time}, Deadline: H{pkg['deadline']}). Muatan kendaraan: {current_load}/{vehicle_capacity}"
                )

        # Perform pickups at the current node (utilizes available capacity)
        pkgs_to_check = sorted(
            [s for s in package_states.values() if s["status"] == "Undelivered" and s["package"]["src"] == current_node],
            key=lambda x: (x["package"]["priority"], x["package"]["deadline"])
        )
        for state in pkgs_to_check:
            pkg = state["package"]
            if current_load + pkg["volume"] <= vehicle_capacity:
                current_load += pkg["volume"]
                state["status"] = "PickedUp"
                state["path"] = [current_node]
                state["details"] = f"Dijemput di Node {current_node} pada waktu {current_time}."
                vehicle_log.append(
                    f" - Paket #{pkg['id']} dijemput di Node {current_node}. Muatan kendaraan: {current_load}/{vehicle_capacity}"
                )

        if action == "return_to_depot":
            has_undelivered_now = any(s["status"] == "Undelivered" for s in package_states.values())
            if has_undelivered_now:
                trip_number += 1
                vehicle_log.append(
                    f"Trip #{trip_number} dimulai: Kendaraan memuat ulang/kembali bersiap di Depot pada waktu {current_time}."
                )

    for pkg_id, state in package_states.items():
        if state["status"] == "Undelivered":
            state["status"] = "Failed_Capacity"
            state["details"] = "Gagal Terkirim (Tidak sempat terangkut hingga simulasi selesai)"

    success_count = sum(1 for s in package_states.values() if s["status"] == "Success")
    failed_count = len(packages) - success_count

    stats = {
        "success_count": success_count,
        "failed_count": failed_count,
        "total_load": sum(p["volume"] for p in packages if package_states[p["id"]]["status"] == "Success"),
        "capacity": vehicle_capacity,
    }

    return {
        "depot_paths": depot_paths,
        "package_paths": list(package_states.values()),
        "vehicle_log": vehicle_log,
        "stats": stats,
        "connectivity": connectivity,
    }
