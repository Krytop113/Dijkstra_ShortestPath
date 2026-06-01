from flask import Flask, render_template, request, session

from controller.graf import generate_random_graph, import_graph_from_csv
from controller.package_manager import (
    add_package,
    clear_packages,
    load_sample_packages,
    remove_package,
)

app = Flask(__name__)
app.secret_key = "dev-secret-key"


def parse_int(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


@app.route("/", methods=["GET", "POST"])
def home():
    num_nodes = session.get("num_nodes", 6)
    depot_node = session.get("depot_node", 0)
    graph = session.get("graph")
    packages = session.get("packages", [])
    package_counter = session.get("package_counter", 1)
    message = None
    message_type = "success"

    if request.method == "POST":
        action = request.form.get("action", "generate_graph")
        num_nodes = parse_int(request.form.get("numNodes"), num_nodes)
        depot_node = parse_int(request.form.get("depotNode"), depot_node)

        if num_nodes < 2:
            message = "Jumlah simpul minimal adalah 2."
            message_type = "err"
        elif num_nodes > 50:
            message = "Jumlah simpul maksimal adalah 50."
            message_type = "err"
        else:
            if depot_node >= num_nodes or depot_node < 0:
                depot_node = 0
                message = "Simpul Depot tidak valid, otomatis diatur ke simpul 0."
                message_type = "err"

            if action == "generate_graph":
                graph = generate_random_graph(num_nodes)
                message = message or "Graf berhasil dibuat."
            elif action == "import_graph":
                graph, message, message_type = import_graph_from_csv(request.files.get("graphFile"))

                if graph is not None:
                    num_nodes = len(graph)
                    if depot_node >= num_nodes:
                        depot_node = 0
                    valid_packages = [
                        package for package in packages
                        if package["src"] < num_nodes and package["dst"] < num_nodes
                    ]
                    if len(valid_packages) != len(packages):
                        message = f"{message} Paket dengan node di luar graf ikut dihapus."
                    packages = valid_packages
            elif action == "add_package":
                packages, package_counter, message, message_type = add_package(
                    packages=packages,
                    package_counter=package_counter,
                    num_nodes=num_nodes,
                    src=parse_int(request.form.get("pkgSrc"), 0),
                    dst=parse_int(request.form.get("pkgDst"), 0),
                    priority=parse_int(request.form.get("pkgPri"), 1),
                    volume=parse_int(request.form.get("pkgVol"), 1),
                    deadline=parse_int(request.form.get("pkgDead"), 1),
                )
            elif action == "remove_package":
                package_id = parse_int(request.form.get("package_id"), 0)
                packages = remove_package(packages, package_id)
                message = "Paket berhasil dihapus."
            elif action == "clear_packages":
                packages, package_counter = clear_packages()
                message = "Semua paket berhasil dihapus."
            elif action == "load_sample_packages":
                if graph is None or len(graph) != num_nodes:
                    graph = generate_random_graph(num_nodes)
                packages, package_counter = load_sample_packages(num_nodes)
                message = "Paket contoh berhasil dimuat."

        session["num_nodes"] = num_nodes
        session["depot_node"] = depot_node
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
    )


if __name__ == "__main__":
    app.run(debug=True)
