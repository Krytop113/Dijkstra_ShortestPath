from flask import Flask, render_template, request

from controller.graf_generator import generate_random_graph

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def home():
    num_nodes = 6
    depot_node = 0
    graph = None
    message = None
    message_type = "success"

    if request.method == "POST":
        try:
            num_nodes = int(request.form.get("numNodes", 6))
            depot_node = int(request.form.get("depotNode", 0))
        except ValueError:
            num_nodes = 6
            depot_node = 0
            message = "Input harus berupa angka."
            message_type = "err"

        if message is None:
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
                else:
                    message = "Graf berhasil dibuat."

                graph = generate_random_graph(num_nodes)

    return render_template(
        "tugas_besar.html",
        depot_node=depot_node,
        graph=graph,
        message=message,
        message_type=message_type,
        num_nodes=num_nodes,
    )


if __name__ == "__main__":
    app.run(debug=True)
