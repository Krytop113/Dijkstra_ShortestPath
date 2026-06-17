def add_package(packages, package_counter, num_nodes, src, dst, priority, volume, deadline):
    if src >= num_nodes or dst >= num_nodes or src < 0 or dst < 0:
        return packages, package_counter, "Node tidak valid.", "err"

    if src == dst:
        return packages, package_counter, "Asal dan tujuan sama.", "err"

    if volume > 100:
        return packages, package_counter, "Volume paket tidak boleh melebihi 100.", "err"


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


def filter_out_of_bounds_packages(packages, num_nodes):
    valid_packages = [
        package for package in packages
        if package["src"] < num_nodes and package["dst"] < num_nodes
    ]
    removed_any = len(valid_packages) != len(packages)
    return valid_packages, removed_any



def load_sample_packages(num_nodes):
    raw_samples = [
        {"priority": 1, "volume": 20, "deadline": 150},
        {"priority": 1, "volume": 30, "deadline": 180},
        {"priority": 2, "volume": 25, "deadline": 300},
        {"priority": 2, "volume": 20, "deadline": 15},
        {"priority": 3, "volume": 5, "deadline": 400},
    ]

    packages = []
    package_counter = 1

    for i, data in enumerate(raw_samples):

        dst = 1 + (i % (num_nodes - 1))

        packages.append({
            "id": package_counter,
            "src": 0,
            "dst": dst,
            "priority": data["priority"],
            "volume": data["volume"],
            "deadline": data["deadline"]
        })
        package_counter += 1

    return packages, package_counter

