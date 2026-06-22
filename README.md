# Dijkstra Shortest Path Simulation

A web-based delivery route simulator built with Flask for the final project in the "Strategi Algoritmik" course. This application lets you create or import an undirected weighted graph, manage delivery packages, and visualize routing decisions using Dijkstra's algorithm.

## 🚀 Features

- Generate a random connected graph with a configurable number of nodes.
- Import a graph from a CSV adjacency matrix.
- Define a depot node and vehicle capacity.
- Add delivery packages with source, destination, priority, volume, and deadline.
- Evaluate package delivery status using Dijkstra-based route planning.
- View routes, delivery logs, package outcomes, and graph connectivity.

## 📁 Project Structure

- `app.py`: Flask application entry point.
- `controller/graf.py`: Graph generation and CSV import logic.
- `controller/dijkstra.py`: Dijkstra algorithm implementation.
- `controller/main.py`: Delivery overview and package routing logic.
- `controller/package_manager.py`: Package CRUD and sample package utilities.
- `templates/`: Flask templates for the UI.
- `static/js/`: Frontend scripts (if present).

## 🛠️ Setup

1. Create and activate a virtual environment (recommended):

```bash
python -m venv .venv
.venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## ▶️ Run the Application

```bash
python app.py
```

Then open the app in your browser:

- `http://127.0.0.1:5000/`

## 🧠 How to Use

1. On the home page, choose to generate a new graph or import a graph from CSV.
2. Set the Depot node and vehicle capacity.
3. Add packages with:
   - `src` (source node)
   - `dst` (destination node)
   - `priority` (1 = highest priority, 3 = lowest priority)
   - `volume`
   - `deadline`
4. Click `Overview` to see the planned routing, Dijkstra steps, and package delivery results.

## 📄 Import Graph CSV Format

The app supports importing an adjacency matrix as a CSV file.

- The matrix must be square with non-negative integer weights.
- The file may optionally begin with a single row containing the node count.
- Example without node count:

```csv
0,10,0,5
10,0,3,0
0,3,0,1
5,0,1,0
```

- Example with node count:

```csv
4
0,10,0,5
10,0,3,0
0,3,0,1
5,0,1,0
```

## 📌 Notes

- Graph node count must be between 2 and 50.
- CSV weights must be non-negative.
- Package source and destination nodes must exist within the graph.
- The route planner uses Dijkstra's algorithm for shortest paths and selects package pickups/deliveries based on priority, capacity, and deadlines.

## 💡 Improvements

This project is designed for demonstration and can be extended with:

- better route optimization for multiple deliveries per trip
- improved package scheduling and load balancing
- richer graph visualization
- support for directed graphs or asymmetric weights

## 📚 Requirements

- Flask

## ✨ License

Use this repository for learning and academic purposes.
