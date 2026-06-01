import csv
import random
from io import StringIO

def generate_random_graph(num_nodes):
    graph = [[0 for _ in range(num_nodes)] for _ in range(num_nodes)]
    visited = [0]
    unvisited = list(range(1, num_nodes))

    while unvisited:
        node_index = random.randrange(len(unvisited))
        u = unvisited.pop(node_index)
        v = random.choice(visited)
        weight = random.randint(5, 44)

        graph[u][v] = weight
        graph[v][u] = weight
        visited.append(u)

    for i in range(num_nodes):
        for j in range(i + 1, num_nodes):
            if graph[i][j] == 0 and random.random() < 0.25:
                weight = random.randint(5, 54)
                graph[i][j] = weight
                graph[j][i] = weight

    return graph


def import_graph_from_csv(uploaded_file):
    if not uploaded_file or uploaded_file.filename == "":
        return None, "Pilih file CSV terlebih dahulu.", "err"

    if not uploaded_file.filename.lower().endswith(".csv"):
        return None, "File harus berformat .csv.", "err"

    try:
        content = uploaded_file.stream.read().decode("utf-8-sig")
        rows = [
            [cell.strip() for cell in row if cell.strip() != ""]
            for row in csv.reader(StringIO(content))
        ]
        rows = [row for row in rows if row]

        if not rows:
            return None, "File CSV kosong.", "err"

        declared_num_nodes = None
        matrix_rows = rows

        if len(rows[0]) == 1 and len(rows) > 1:
            declared_num_nodes = int(rows[0][0])
            matrix_rows = rows[1:]

        graph = [[int(cell) for cell in row] for row in matrix_rows]
        num_nodes = len(graph)

        if declared_num_nodes is not None and declared_num_nodes != num_nodes:
            return None, "Jumlah baris matrix tidak sesuai dengan jumlah simpul di baris pertama.", "err"

        if num_nodes < 2:
            return None, "Jumlah simpul minimal adalah 2.", "err"

        if num_nodes > 50:
            return None, "Jumlah simpul maksimal adalah 50.", "err"

        if any(len(row) != num_nodes for row in graph):
            return None, "Matrix CSV harus berbentuk persegi.", "err"

        if any(weight < 0 for row in graph for weight in row):
            return None, "Bobot graf tidak boleh bernilai negatif.", "err"

        return graph, "Graf berhasil diimpor dari CSV.", "success"
    except UnicodeDecodeError:
        return None, "File CSV harus berupa teks UTF-8.", "err"
    except ValueError:
        return None, "Isi CSV harus berupa angka.", "err"
    except Exception as error:
        return None, f"Terjadi kesalahan saat mengimpor graf: {error}", "err"
