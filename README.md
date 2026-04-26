*This project has been created as part of the 42 curriculum by berrabia.*

# Fly-In

## Description
Fly-In is a Python and Pygame simulation that routes a fleet of drones from a unique start hub to a unique target hub through a connected graph of zones.

The goal of the project is to deliver every drone in the fewest possible simulation turns while respecting the rules of the network:
- zone capacity through `max_drones`
- connection capacity through `max_link_capacity`
- zone types such as `normal`, `priority`, `restricted`, and `blocked`
- turn-by-turn movement and waiting when movement is not possible

The project parses a text map, builds the graph, simulates drone decisions turn by turn, and displays the network in a graphical window.

## Instructions
### Requirements
- Python 3.10 or later
- `pygame`

### Installation
Create and activate a virtual environment if you want an isolated setup:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pygame
```

### Run
Launch the simulation by giving a map file as the argument:

```bash
python main.py maps/easy/01_linear_path.txt
```

You can try any of the provided maps inside `maps/easy`, `maps/medium`, `maps/hard`, or `maps/challenger`.

### Map format overview
Each map file contains:
- `nb_drones: <number>`
- one `start_hub`
- one `end_hub`
- zero or more regular `hub` entries
- bidirectional `connection` entries
- optional metadata in brackets, such as `color`, `zone`, `max_drones`, and `max_link_capacity`

## Features
- Parses the custom Fly-In map format
- Builds a bidirectional graph of hubs and connections
- Simulates multiple drones at the same time
- Respects hub and link capacity constraints
- Supports waiting when no useful move is available
- Handles restricted zones as multi-turn movement
- Draws the graph, the drones, and animated start/end flags in a Pygame window
- Prints one movement line per simulation turn

## Workflow and Algorithm
The workflow starts in `parsing`, which reads the map file, extracts `nb_drones`, `start_hub`, `end_hub`, `hub`, and `connections` entries, and returns the hub list, the connection list, and the two special endpoints; after that, `main` creates the `Graph`, fills it with `Graph.init_the_graph`, places each hub on the window, creates one `Drone` per requested unit, and computes a reverse distance table with `build_static_distance_map` so every hub has a fast estimate of how far it is from the target; the simulation then runs in discrete turns, and each turn first resolves drones already traveling by decrementing `turns_remaining`, releasing the reserved link with `graph.release_edge`, moving the drone to the arrival hub, and marking it as finished if it reached `target_hub`; once the moving drones are updated, the scheduler examines each idle drone, uses `rank_next_hubs` to filter legal neighbors with the static distance map, `graph.edge_available`, `Hub.can_enter_hub`, blocked-zone checks, and a small revisit penalty based on `passed_hubs`, keeps only the best candidates, and chooses the next move; if the destination is a normal hub, the drone moves immediately, updates its current hub and occupancy, and the turn is recorded, but if the destination is a restricted hub the drone enters multi-turn travel by setting `in_transit`, `turns_remaining`, `current_target`, and `active_edge`, while `graph.reserve_edge` keeps the connection locked until arrival; after all decisions are collected, `Drawing_Animation_Methods.animate_movements` interpolates the sprite positions frame by frame and `Drawing_Animation_Methods.draw_scene` redraws the full scene with hubs, connections, drones, and the animated flags from `draw_flags`, so the whole scheduler stays deterministic, greedy, and easy to follow because every choice is driven by the precomputed distance-to-target values plus live capacity checks rather than by random path selection.

## Visual Representation
The project uses Pygame to present the simulation visually.

### What is shown
- hubs are drawn as colored circles
- connections are drawn as lines with colors depending on the zone
- drones are rendered as sprites moving between hubs
- animated flags mark the start and target hubs
- the current turn is displayed on screen

### Why it helps
The visual layer makes it easier to understand:
- which hubs are crowded
- where drones are waiting
- how the scheduler distributes drones across paths
- when a drone is forced to wait because of capacity
- how restricted zones slow the route

This feedback is useful when tuning the routing strategy because it shows both the final path decisions and the timing of each move.

## Resources
### References
- Python documentation: https://docs.python.org/3/
- Pygame documentation: https://www.pygame.org/docs/
- Dijkstra's algorithm overview: https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm
- Graph theory basics: https://en.wikipedia.org/wiki/Graph_theory
- Multi-agent path finding overview: https://en.wikipedia.org/wiki/Multi-agent_pathfinding
- 42 Fly-In subject PDF included in this repository

### AI usage
AI was used as a support tool for:
- interpreting the assignment requirements
- comparing possible routing strategies
- drafting and refining the README structure
- checking the explanation of the algorithm and visual choices
- helping identify where the implementation should be described more clearly

The code, map validation, and final design decisions were reviewed and adjusted manually in the repository.
