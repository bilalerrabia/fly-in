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

## Algorithm Choices and Implementation Strategy
The current implementation uses a centralized, turn-based scheduler.

### 1. Graph construction
The map is parsed into a graph where each hub becomes a node and each connection becomes a bidirectional edge. Connection capacities are stored separately so the scheduler can reserve and release them during the simulation.

### 2. Shortest-path recomputation
Each idle drone recomputes its shortest path from the current hub to the target hub on every turn. The final move choice is then filtered through a static shortest-distance map, which rejects dead-end hubs and keeps the drone moving toward the target.

### 3. Next-move selection
The scheduler then tries to launch drones in turn order. It checks the current shortest-path candidates, keeps only the three best next hubs, filters out dead-end routes, rejects blocked or full destinations, reserves the connection, and prints exactly one movement line for the turn.

The decision rule is intentionally simple:
- prefer the next hub with the smallest remaining distance to the target
- respect hub capacity and connection capacity before launching a move
- only move when one of the top three shortest candidates is available and still has a real route to the target
- reserve restricted zones across turns so they cannot be overbooked
- if no move is possible, the drone waits

This keeps the behavior deterministic and prevents the drones from taking random detours while still adapting to the live turn state.

### 4. Turn scheduling
The simulation runs in discrete turns.
- drones that are already traveling finish their transit first
- then the router chooses moves for idle drones
- capacities are updated immediately when a move starts
- the turn ends after all movements for that frame are resolved

### 5. Restricted zones
Restricted zones are treated as longer movements. They are animated and resolved over multiple turns, which matches the subject's movement-cost rules.

### 6. Trade-offs
This is a greedy, centralized scheduler rather than a full multi-agent pathfinding solver. That makes it easier to understand and maintain, while still being effective on the provided maps. The main trade-off is that it does not guarantee a globally optimal solution for every possible graph, but it gives a practical and explainable strategy for the project.

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
