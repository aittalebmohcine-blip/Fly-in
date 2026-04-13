*This project has been created as part of the 42 curriculum by mait-tal.*

# Fly_in

## Description
I built a drone route simulation that reads a structured configuration file and simulates deliveries across a small network of zones.

The program parses a map definition with `start_hub`, `end_hub`, regular `hub` zones, and bidirectional `connection` links. Each zone can include metadata such as type, capacity, and display color. I then compute valid routes, sort them by cost and priority, and assign routes to drones before running a turn-based simulation.

## Instructions

### Requirements
- Python 3
- `pydantic`
- `termcolor`

You can install dependencies with:

```bash
pip install -r requirements.txt
```

### Run the project

From the repository root, run:

```bash
python3 fly_in.py <config-file>
```

For example:

```bash
python3 fly_in.py maps/easy/01_linear_path.txt
```

Alternatively, use the Makefile commands for convenience:

- `make install`: Install dependencies from requirements.txt
- `make run`: Run the simulation on all map files in the maps/ directory
- `make debug`: Run the simulation in debug mode with pdb on the default config (maps/easy/01_linear_path.txt)
- `make clean`: Clean up __pycache__ and .mypy_cache directories
- `make lint`: Run linting with flake8 and mypy (excludes venv directory if present)

### Input format

The config file must start with:

```text
nb_drones: <number>
```

Then it can include zone definitions like:

```text
start_hub: A 0 0 [type=normal color=green max_drones=2]
hub: B 1 0 [type=priority color=yellow]
end_hub: Z 2 0
```

And connection definitions like:

```text
connection: A-B
connection: B-Z [max_link_capacity=2]
```

Comments beginning with `#` are ignored.

## Algorithm choices and implementation strategy

I focused on a few clear steps:

1. **Parsing and validation**
   - I parse every line and reject invalid formats or duplicate definitions.
   - I validate `nb_drones` first, require exactly one `start_hub` and `end_hub`, and verify connections reference existing zones.

2. **Graph construction**
   - I store zones and connections in a map model.
   - I build an undirected adjacency list for the network.

3. **Route discovery**
   - I compute all simple paths from start to end using a path search over the graph.
   - I remove the `start` node from assigned routes because drones already begin there.

4. **Route scoring**
   - I filter out routes with blocked zones.
   - I increase the route cost for restricted zones.
   - I sort remaining routes by cost and by the number of priority zones.

5. **Drone assignment and simulation**
   - I assign drones to routes based on the sorted, filtered path list.
   - The simulation advances turn by turn until every drone reaches the end.

## Visual representation features

The simulation prints colored terminal output so I can track drone movement and zone states.

- Drones are shown with their current location.
- Zone colors are applied when available.
- This color-based feedback helps me see route progress and identify restricted or normal zone transitions.

## Resources

- Python documentation: https://docs.python.org/3/
- Pydantic: https://pydantic-docs.helpmanual.io/
- Termcolor: https://pypi.org/project/termcolor/
- Graph traversal concepts: depth-first and breadth-first search

## AI usage

I used AI to help write and organize documentation, and to improve comments in the code. The algorithm logic and the implementation details remain based on my own project design.
