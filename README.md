*This project has been created as part of the 42 curriculum by berrabia.*

# Fly-In

## Description
Fly-In is a Python and Pygame simulation that moves a fleet of drones from a unique start hub to a unique target hub through a custom graph of hubs, connections, and zones.

Each map describes:
- the number of drones to simulate
- the start and end hubs
- regular hubs with coordinates and optional metadata
- bidirectional connections between hubs

The program parses the map, builds an undirected graph, computes a reverse distance map from the target hub, and then runs a turn-based greedy scheduler that chooses the next legal move for each drone. The scene is rendered in a Pygame window with animated drones, connections, and flags so the result is easy to inspect turn by turn.

The simulation also prints one movement line per turn in the terminal, which makes it easy to compare the textual trace with the visual animation.

## Instructions
### Requirements
- Python 3.10 or newer
- `pygame`

### Installation
The simplest way to install the only external dependency is through the Makefile:

```bash
make install
```

If you prefer a virtual environment:

```bash
python3 -m virtualenv .venv
source .venv/bin/activate
pip install pygame
```

### Run
Use any map file from the `maps/` directory:

```bash
python3 main.py maps/easy/01_linear_path.txt
```

The repository also provides a default benchmark target:

```bash
make run
```

Useful helper targets:

```bash
make debug
make lint
make lint-strict
```

### Map Format
The parser accepts the following structure:

- `nb_drones: <number>` must appear first
- one `start_hub`
- one `end_hub`
- any number of regular `hub` lines
- `connection` lines linking two named hubs with `name1-name2`
- optional metadata in brackets, for example `color`, `zone`, `max_drones`, and `max_link_capacity`

Example:

```text
nb_drones: 2
start_hub: start 0 0 [color=green]
hub: waypoint1 1 0 [color=blue]
hub: waypoint2 2 0 [color=blue]
end_hub: goal 3 0 [color=red]

connection: start-waypoint1
connection: waypoint1-waypoint2
connection: waypoint2-goal
```

Notes:
- `zone` can be `blocked`, `normal`, `restricted`, or `priority`
- `max_drones` controls hub occupancy
- for `start_hub` and `end_hub`, `max_drones` defaults to `nb_drones` when it is omitted

## Algorithm and Implementation Strategy
The implementation is intentionally greedy and local rather than a full multi-agent search.

1. `Parsing.parsing()` reads the map path from `sys.argv[1]`, strips comments, validates the syntax, rejects duplicate or inconsistent declarations, and returns the hub list, connection list, start hub, target hub, and drone count.
2. `Graph(hubs, connections)` turns the parsed tuples into an undirected adjacency list. `Hub.get_cost()` assigns the zone cost used by the scheduler: blocked is infinite, priority is 0.5, normal is 1, and restricted is 2.
3. `Solver.build_static_distance_map()` computes a reverse Dijkstra-style distance map from the target hub. The result gives each reachable hub a cheap estimate of how far it is from the goal, while blocked hubs are ignored.
4. On every turn, `main()` first clears drones that were marked `in_transit` on the previous turn, then it scans idle drones and asks `Solver.rank_next_hubs()` for the neighbors that are not farther from the target and still satisfy `Hub.can_enter_hub()`.
5. The scheduler chooses the first ranked legal move, updates hub occupancy counters, records the destination in `current_target`, and marks drones entering restricted hubs as `in_transit` so the turn bookkeeping stays consistent.
6. `Rendring.draw_turn()` animates the move over 30 frames at 60 FPS, interpolating each drone position frame by frame while redrawing the full scene.


## Visual Representation
The renderer in `render.py` turns the simulation into a readable live view.

- hubs are drawn as colored circles
- connections are drawn as lines with a zone-based palette
- drones are rendered as sprites loaded from `photos/`
- animated flags mark the start and target hubs
- the current turn number is shown in the top-left corner

The layout is computed from the map coordinates, centered in a 1700x1000 window, and the movement between hubs is interpolated smoothly so each turn is visible instead of jumping instantly. This makes it much easier to see:
- where congestion builds up
- which hubs are available
- how the greedy ranking progresses toward the target
- when a drone is waiting because it has no legal move

## Resources
### References
- Pygame documentation: https://www.pygame.org/docs/
- Dijkstra's algorithm: https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm
- Graph theory basics: https://en.wikipedia.org/wiki/Graph_theory
- Multi-agent pathfinding overview: https://en.wikipedia.org/wiki/Multi-agent_pathfinding
- The Fly-In subject from the 42 curriculum

### AI usage
README hh
