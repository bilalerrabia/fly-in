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
The live workflow starts in `parsing`, which reads the map file from `sys.argv[1]`, skips blank lines and comments, parses `nb_drones`, `start_hub`, `end_hub`, `hub`, and `connection` entries, extracts optional metadata such as `color`, `zone`, `max_drones`, and `max_link_capacity`, and returns the hub list, the connection list, the start hub, the target hub, and the drone count; `main` then computes the average map coordinates so it can place every `Hub` on the Pygame window, builds the network with `Graph(hubs, connections)`, which internally resolves names with `Hub.get_hub` and creates the bidirectional edges with `Edge.add_edge`, and precomputes a reverse distance map with `build_static_distance_map` so every hub has a cheap estimate of how far it is from `target_hub`; after that, `main` creates one `Drone` per requested unit, initializes the start occupancy count, and enters a turn loop where the first pass resolves drones that are already traveling by decrementing `turns_remaining`, releasing `active_edge` with `graph.release_edge` when the move is finished, moving the drone onto its arrival hub, updating `corrent_hub`, `corrent_position`, `display_position`, `current_target`, and `passed_hubs`, and marking `reach_target` when the drone reaches the goal; the second pass handles idle drones by calling `rank_next_hubs`, which filters neighbors using the static distance map, `graph.edge_available`, `Hub.can_enter_hub`, blocked-zone checks, and a revisit penalty based on `passed_hubs`, then sorts the legal candidates and lets the scheduler pick the best move from the first three; if the destination is a normal hub, the drone moves immediately, updates the hub occupancy counters, appends the hub to `passed_hubs`, and the edge is released after the turn, but if the destination is a restricted hub the drone enters a multi-turn move by setting `in_transit`, `turns_remaining`, `current_target`, `transit_connection_name`, and `active_edge`, reserving the edge until arrival and animating the movement toward the midpoint; once all move decisions are collected, `Rendring.animate_movements` interpolates the drone sprites frame by frame, `Rendring.draw_scene` redraws the whole scene with the connections, hubs, drones, text, and the animated flags from `draw_flags`, and the result is a deterministic greedy scheduler: instead of recomputing a full path for every drone on every turn, it uses one reverse distance table plus live capacity checks to keep every move simple, legal, and predictable.

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
