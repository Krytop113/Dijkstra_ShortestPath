from controller.dijkstra import dijkstra, reconstruct_path, check_graph_connectivity

VEHICLE_CAPACITY = 100

def get_dijkstra_overview(graph, packages, depot_node):
    if not graph:
        return {
            "depot_paths": [],
            "package_paths": [],
            "vehicle_log": [],
            "stats": {},
            "connectivity": {},
        }

    num_nodes = len(graph)

    # 1. Hitung Jalur Terpendek Statis dari Depot ke Semua Simpul (untuk tabel referensi)
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

    # 2. Pengecekan Konektivitas Graf
    connectivity = check_graph_connectivity(graph, depot_node)

    # 3. Inisialisasi Status Paket
    # Status bisa berupa: "Undelivered", "PickedUp", "Delivered", "Failed_Capacity", "Failed_Deadline", "Failed_Unreachable"
    package_states = {}
    for pkg in packages:
        pkg_id = pkg["id"]
        # Validasi awal: volume melebihi kapasitas kendaraan
        if pkg["volume"] > VEHICLE_CAPACITY:
            package_states[pkg_id] = {
                "package": pkg,
                "status": "Failed_Capacity",
                "details": f"Gagal Terkirim (Volume paket {pkg['volume']} melebihi kapasitas kendaraan {VEHICLE_CAPACITY})",
                "arrival_time": None,
                "path": None,
            }
        # Validasi awal: asal/tujuan tidak terhubung dari depot
        elif depot_dist[pkg["src"]] >= 10**9:
            package_states[pkg_id] = {
                "package": pkg,
                "status": "Failed_Unreachable",
                "details": f"Gagal Terkirim (Asal paket simpul {pkg['src']} tidak dapat dijangkau dari Depot)",
                "arrival_time": None,
                "path": None,
            }
        else:
            # Periksa jalur dari src ke dst
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
                    "path": [], # Melacak jalur fisik yang dilewati paket ini saja
                }

    # 4. Memulai Simulasi Perutean Logistik (Pickup & Delivery + Multi-Trip + Heuristik)
    current_node = depot_node
    current_time = 0
    current_load = 0
    
    trip_number = 1
    vehicle_log = [
        f"Trip #{trip_number} dimulai: Kendaraan berangkat dari Depot (Node {depot_node}) pada waktu 0. Muatan: 0/{VEHICLE_CAPACITY}"
    ]

    while True:
        # Tentukan kandidat tujuan berikutnya
        candidates = [] # berisi tuple (node_target, jenis_aksi)
        
        for pkg_id, state in package_states.items():
            pkg = state["package"]
            if state["status"] == "Undelivered":
                # Bisa dijemput jika kapasitas kendaraan cukup
                if current_load + pkg["volume"] <= VEHICLE_CAPACITY:
                    candidates.append((pkg["src"], "pickup"))
            elif state["status"] == "PickedUp":
                # Harus diantar ke tujuan
                candidates.append((pkg["dst"], "delivery"))

        # Jika tidak ada paket yang aktif untuk dijemput/diantar, tapi kendaraan tidak berada di depot
        # dan masih ada paket Undelivered yang tersisa (yang mungkin belum muat sebelumnya), kembali ke depot untuk trip baru.
        has_undelivered = any(s["status"] == "Undelivered" for s in package_states.values())
        if not candidates:
            if current_node != depot_node:
                candidates.append((depot_node, "return_to_depot"))
            else:
                # Kendaraan sudah di depot dan tidak ada lagi yang bisa dijemput/diantar
                break

        # Cari jarak terpendek dari posisi saat ini ke semua simpul
        dist, prev = dijkstra(graph, current_node)

        # Evaluasi kandidat menggunakan fungsi heuristik untuk memilih tujuan terbaik
        best_candidate = None
        best_score = -float("inf")
        best_path = None
        best_dist = None

        for target_node, action in candidates:
            d_to_target = dist[target_node]
            if d_to_target >= 10**9:
                continue # Simpul target tidak dapat dijangkau dari posisi saat ini
                
            # Hitung skor heuristik dasar (mengutamakan jarak yang lebih dekat)
            score = -d_to_target
            
            if action == "pickup":
                # Dapatkan semua paket di simpul ini yang siap dijemput
                pkgs_here = [
                    s["package"] for s in package_states.values()
                    if s["status"] == "Undelivered" and s["package"]["src"] == target_node and current_load + s["package"]["volume"] <= VEHICLE_CAPACITY
                ]
                # Beri bonus prioritas dan urgensi deadline
                for p in pkgs_here:
                    score += (4 - p["priority"]) * 30 # Prioritas lebih tinggi (P1=90, P2=60, P3=30)
                    eta = current_time + d_to_target
                    if eta <= p["deadline"]:
                        # Semakin dekat ke deadline (sedikit sisa waktu), semakin tinggi urgensinya
                        score += max(0, 100 - (p["deadline"] - eta) * 5)
                    else:
                        score -= 50 # Sudah terlambat, kurangi urgensi jemput
                        
            elif action == "delivery":
                # Mengantar paket sangat diutamakan untuk membebaskan kapasitas kendaraan
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
                        score -= 100 # Terlambat, penalti skor
                        
            elif action == "return_to_depot":
                # Kembali ke depot diberi penalti kecil agar dihindari jika masih ada aksi lain
                score -= 40
                if current_load > 0:
                    # Jangan kembali ke depot jika masih membawa paket yang bisa dikirim
                    score -= 500

            if score > best_score:
                best_score = score
                best_candidate = (target_node, action)
                best_dist = d_to_target
                best_path = reconstruct_path(prev, current_node, target_node)

        # Jika tidak ada simpul target yang dapat dijangkau
        if best_candidate is None:
            # Semua paket aktif yang tersisa ditandai gagal karena tidak dapat dijangkau
            for pkg_id, state in package_states.items():
                if state["status"] in ["Undelivered", "PickedUp"]:
                    state["status"] = "Failed_Unreachable"
                    state["details"] = "Gagal Terkirim (Tujuan/Asal terisolasi dari rute kendaraan)"
            vehicle_log.append(
                f"Kendaraan berhenti di Node {current_node}. Sisa paket tidak dapat dijangkau dari posisi saat ini."
            )
            break

        target_node, action = best_candidate
        
        # Perbarui waktu dan bergerak ke simpul terpilih
        current_time += best_dist
        path_str = " -> ".join(map(str, best_path))
        
        # Tambahkan pergerakan ke jalur masing-masing paket yang sedang diangkut
        for state in package_states.values():
            if state["status"] == "PickedUp":
                # Tambahkan jalur pergerakan kendaraan (kecuali simpul awal untuk menghindari duplikasi)
                state["path"].extend(best_path[1:])

        if action == "return_to_depot":
            vehicle_log.append(
                f"Kendaraan kembali ke Depot (Node {target_node}) melalui jalur [{path_str}] (Jarak: {best_dist}). Waktu kumulatif: {current_time}."
            )
            current_node = target_node
            # Mulai Trip baru jika masih ada paket yang perlu dijemput
            if has_undelivered:
                trip_number += 1
                vehicle_log.append(
                    f"Trip #{trip_number} dimulai: Kendaraan memuat ulang/kembali bersiap di Depot pada waktu {current_time}."
                )
            continue

        vehicle_log.append(
            f"Kendaraan bergerak dari Node {current_node} ke Node {target_node} melalui jalur [{path_str}] (Jarak: {best_dist}). Waktu kumulatif: {current_time}."
        )
        current_node = target_node

        # Lakukan aksi di simpul tujuan
        if action == "delivery":
            # 1. Antar paket yang tujuannya simpul ini
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
                        f" - Paket #{pkg_id} berhasil terkirim ke Node {current_node} tepat waktu (Tiba: {current_time}, Deadline: H{pkg['deadline']}). Muatan kendaraan: {current_load}/{VEHICLE_CAPACITY}"
                    )
                else:
                    state["status"] = "Failed_Deadline"
                    state["details"] = f"Gagal Terkirim (Terlambat: Waktu tiba {current_time}, Deadline: H{pkg['deadline']})"
                    vehicle_log.append(
                        f" - Paket #{pkg_id} GAGAL terkirim ke Node {current_node} karena terlambat (Tiba: {current_time}, Deadline: H{pkg['deadline']}). Muatan kendaraan: {current_load}/{VEHICLE_CAPACITY}"
                    )

        elif action == "pickup":
            # 2. Jemput paket yang asalnya simpul ini (selama kapasitas muat)
            pickups_here = [
                pkg_id for pkg_id, s in package_states.items()
                if s["status"] == "Undelivered" and s["package"]["src"] == current_node and current_load + s["package"]["volume"] <= VEHICLE_CAPACITY
            ]
            for pkg_id in pickups_here:
                state = package_states[pkg_id]
                pkg = state["package"]
                current_load += pkg["volume"]
                state["status"] = "PickedUp"
                state["path"] = [current_node] # Inisialisasi awal lintasan paket
                state["details"] = f"Dijemput di Node {current_node} pada waktu {current_time}."
                vehicle_log.append(
                    f" - Paket #{pkg_id} dijemput di Node {current_node}. Muatan kendaraan: {current_load}/{VEHICLE_CAPACITY}"
                )

    # 5. Rekap Paket yang tersisa dan tidak sempat terjemput
    for pkg_id, state in package_states.items():
        if state["status"] == "Undelivered":
            # Jika masih undelivered, kemungkinan karena batasan deadline/waktu atau kapasitas trip habis
            state["status"] = "Failed_Capacity"
            state["details"] = "Gagal Terkirim (Tidak sempat terangkut hingga simulasi selesai)"

    # 6. Hitung Statistik Akhir
    success_count = sum(1 for s in package_states.values() if s["status"] == "Success")
    failed_count = len(packages) - success_count

    stats = {
        "success_count": success_count,
        "failed_count": failed_count,
        "total_load": sum(p["volume"] for p in packages if package_states[p["id"]]["status"] == "Success"),
        "capacity": VEHICLE_CAPACITY,
    }

    return {
        "depot_paths": depot_paths,
        "package_paths": list(package_states.values()),
        "vehicle_log": vehicle_log,
        "stats": stats,
        "connectivity": connectivity,
    }

