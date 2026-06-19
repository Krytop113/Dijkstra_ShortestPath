from flask import Flask, render_template, request, session

from controller.graf import import_graph_from_csv, create_graph_with_validation
from controller.package_manager import (
    add_package,
    clear_packages,
    load_sample_packages,
    remove_package,
    filter_out_of_bounds_packages,
)
from controller.main import get_dijkstra_overview
from controller.dijkstra import dijkstra_with_steps

app = Flask(__name__)
app.secret_key = "dev-secret-key"

def parse_int(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def parse_positive_int(value, default):
    parsed = parse_int(value, default)
    return parsed if parsed > 0 else default


@app.route("/", methods=["GET", "POST"])
def home():
    num_nodes = session.get("num_nodes", 6)
    depot_node = session.get("depot_node", 0)
    vehicle_capacity = session.get("vehicle_capacity", 100)
    graph = session.get("graph")
    packages = session.get("packages", [])
    package_counter = session.get("package_counter", 1)
    message = None
    message_type = "success"

    if request.method == "POST":
        action = request.form.get("action", "generate_graph")
        num_nodes = parse_int(request.form.get("numNodes"), num_nodes)
        depot_node = parse_int(request.form.get("depotNode"), depot_node)
        vehicle_capacity = parse_positive_int(request.form.get("vehicleCapacity"), vehicle_capacity)

        if action == "generate_graph":
            graph, depot_node, message, message_type = create_graph_with_validation(num_nodes, depot_node)
            if graph is not None:
                packages, removed_any = filter_out_of_bounds_packages(packages, num_nodes)
                if removed_any:
                    message = f"{message} Paket dengan node di luar graf ikut dihapus."
        elif action == "import_graph":
            graph, message, message_type = import_graph_from_csv(request.files.get("graphFile"))
            if graph is not None:
                num_nodes = len(graph)
                if depot_node >= num_nodes or depot_node < 0:
                    depot_node = 0
                packages, removed_any = filter_out_of_bounds_packages(packages, num_nodes)
                if removed_any:
                    message = f"{message} Paket dengan node di luar graf ikut dihapus."
        elif action == "add_package":
            if graph is None:
                message = "Silakan generate graf atau import CSV terlebih dahulu sebelum menambahkan paket."
                message_type = "err"
            else:
                packages, package_counter, message, message_type = add_package(
                    packages=packages,
                    package_counter=package_counter,
                    num_nodes=num_nodes,
                    vehicle_capacity=vehicle_capacity,
                    src=parse_int(request.form.get("pkgSrc"), 0),
                    dst=parse_int(request.form.get("pkgDst"), 0),
                    priority=parse_int(request.form.get("pkgPri"), 1),
                    volume=parse_int(request.form.get("pkgVol"), 1),
                    deadline=parse_int(request.form.get("pkgDead"), 1),
                )
        elif action == "update_capacity":
            message = f"Kapasitas kendaraan berhasil diubah menjadi {vehicle_capacity}."
        elif action == "remove_package":
            package_id = parse_int(request.form.get("package_id"), 0)
            packages = remove_package(packages, package_id)
            message = "Paket berhasil dihapus."
        elif action == "clear_packages":
            packages, package_counter = clear_packages()
            message = "Semua paket berhasil dihapus."
        elif action == "load_sample_packages":
            if graph is None:
                message = "Silakan generate graf atau import CSV terlebih dahulu sebelum memuat paket contoh."
                message_type = "err"
            else:
                packages, package_counter = load_sample_packages(num_nodes)
                message = "Paket contoh berhasil dimuat."


        session["num_nodes"] = num_nodes
        session["depot_node"] = depot_node
        session["vehicle_capacity"] = vehicle_capacity
        session["graph"] = graph
        session["packages"] = packages
        session["package_counter"] = package_counter

    return render_template(
        "tugas_besar.html",
        depot_node=depot_node,
        graph=graph,
        message=message,
        message_type=message_type,
        num_nodes=num_nodes,
        packages=packages,
        vehicle_capacity=vehicle_capacity,
    )

@app.route("/overview")
def overview():
    graph = session.get("graph")
    packages = session.get("packages", [])
    depot_node = session.get("depot_node", 0)
    vehicle_capacity = session.get("vehicle_capacity", 100)

    if not graph:
        return render_template(
            "tugas_besar.html",
            depot_node=depot_node,
            graph=graph,
            message="Silakan buat atau impor graf terlebih dahulu sebelum melihat overview.",
            message_type="err",
            num_nodes=session.get("num_nodes", 6),
            packages=packages,
            vehicle_capacity=vehicle_capacity,
        )

    results = get_dijkstra_overview(graph, packages, depot_node, vehicle_capacity)
    _, _, dijkstra_steps = dijkstra_with_steps(graph, depot_node)

    return render_template(
        "overview.html",
        depot_node=depot_node,
        graph=graph,
        depot_paths=results["depot_paths"],
        package_paths=results["package_paths"],
        vehicle_log=results["vehicle_log"],
        stats=results["stats"],
        connectivity=results["connectivity"],
        dijkstra_steps=dijkstra_steps,
        num_nodes=len(graph),
    )


if __name__ == "__main__":
    app.run(debug=True)
