def add_package(packages, package_counter, num_nodes, src, dst, priority, volume, deadline):
    if src >= num_nodes or dst >= num_nodes or src < 0 or dst < 0:
        return packages, package_counter, "Node tidak valid.", "err"

    if src == dst:
        return packages, package_counter, "Asal dan tujuan sama.", "err"

    package = {
        "id": package_counter,
        "src": src,
        "dst": dst,
        "priority": priority,
        "volume": volume,
        "deadline": deadline,
    }

    return [*packages, package], package_counter + 1, "Paket berhasil ditambahkan.", "success"


def remove_package(packages, package_id):
    return [package for package in packages if package["id"] != package_id]


def clear_packages():
    return [], 1


def load_sample_packages(num_nodes):
    sample_data = [
        {"src": 0, "dst": 5, "priority": 1, "volume": 25, "deadline": 4},
        {"src": 0, "dst": 10, "priority": 2, "volume": 30, "deadline": 8},
        {"src": 0, "dst": 3, "priority": 1, "volume": 15, "deadline": 3},
        {"src": 0, "dst": 15, "priority": 3, "volume": 20, "deadline": 12},
        {"src": 0, "dst": 7, "priority": 2, "volume": 18, "deadline": 6},
        {"src": 0, "dst": 12, "priority": 1, "volume": 22, "deadline": 5},
        {"src": 0, "dst": 9, "priority": 3, "volume": 35, "deadline": 15},
        {"src": 0, "dst": 18, "priority": 2, "volume": 28, "deadline": 10},
        {"src": 0, "dst": 6, "priority": 1, "volume": 12, "deadline": 2},
        {"src": 0, "dst": 14, "priority": 2, "volume": 40, "deadline": 9},
    ]

    packages = []
    package_counter = 1

    for data in sample_data:
        if data["dst"] < num_nodes:
            packages.append({"id": package_counter, **data})
            package_counter += 1

    return packages, package_counter
