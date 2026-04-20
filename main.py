import sys
import pygame
from heapq import heappop, heappush
from itertools import count
from math import inf
from time import sleep

from some_parameters import colors
from classes import Hub, Graph, Edge, Drone
from dijkstra import djikstra
from draw_flags import draw_flags

def parse_metadata(line: str):
    metadata = {}
    if "[" in line and "]" in line:
        meta_data_str = line[line.find("[") + 1: line.find("]")]
        meta_data_list = meta_data_str.split()
        metadata = {
            meta_data_list[i].split("=")[0]: meta_data_list[i].split("=")[1]
            for i in range(len(meta_data_list))
            if "=" in meta_data_list[i]
        }
    return metadata


def parse_connection(line: str):
    connection_name = line.split()[1]
    first, second = connection_name.split("-")
    metadata = parse_metadata(line)
    capacity = int(metadata.get("max_link_capacity", 1))
    return first, second, capacity, connection_name


def get_hub(name, hubs):
    for hub in hubs:
        if hub.name == name:
            return hub


def is_there(name: str, list_hubs: list[Edge]):
    for edge in list_hubs:
        if name == edge.target.name:
            return True
    return False


def add_edge(graph: Graph, hub1: Hub, hub2: Hub, capacity: int = 1):
    graph.add_link(hub1, hub2, capacity)
    if graph.nodes.get(hub1, None) is None:
        edge = Edge(hub2.cost, hub2, capacity)
        graph.nodes[hub1] = [edge]
    else:
        edge = Edge(hub2.cost, hub2, capacity)
        if not is_there(hub2.name, graph.nodes[hub1]):
            graph.nodes[hub1].append(edge)


def draw_hubs(window, hubs):
    for hub in hubs:
        if hub.color == "none" or hub.color not in colors:
            pygame.draw.circle(window, colors["green"], (hub.position_on_window[0], hub.position_on_window[1]), 20)
        else:
            pygame.draw.circle(window, colors[hub.color], (hub.position_on_window[0], hub.position_on_window[1]), 20)


def draw_connections(window, connections, hubs):
    for connection in connections:
        first_hub = get_hub(connection[0], hubs)
        second_hub = get_hub(connection[1], hubs)
        if first_hub.zone == "blocked":
            color = colors["red"]
        elif first_hub.zone == "priority":
            color = colors["green"]
        elif first_hub.zone == "restricted":
            color = colors["darkred"]
        else:
            color = colors["white"]
        
        pygame.draw.line(
            window, color,
            first_hub.position_on_window,
            second_hub.position_on_window,
            width=3
        )


def init_the_graph(graph: Graph, hubs: list, connections: list):
    for connection in connections:
        hub1 = get_hub(connection[0], hubs)
        hub2 = get_hub(connection[1], hubs)
        capacity = connection[2]
        add_edge(graph, hub1, hub2, capacity)
        add_edge(graph, hub2, hub1, capacity)


def build_connection_labels(connections: list[tuple[str, str, int, str]]):
    connection_labels: dict[frozenset[str], str] = {}
    for first, second, _, label in connections:
        connection_labels[frozenset((first, second))] = label
    return connection_labels


def can_enter_hub(hub: Hub, start_hub: Hub, target_hub: Hub) -> bool:
    if hub in (start_hub, target_hub):
        return True
    if hub.zone == "blocked":
        return False
    return hub.corrent_number_of_drones < hub.max_drones


def make_cost_func(start_hub: Hub, target_hub: Hub):
    def cost_func(hub: Hub):
        if hub.zone == "blocked":
            return float("inf")
        if hub not in (start_hub, target_hub) and hub.corrent_number_of_drones >= hub.max_drones:
            return float("inf")
        return hub.cost + (hub.corrent_number_of_drones / max(1, hub.max_drones)) * 10

    return cost_func


def build_static_distance_map(graph: Graph, hubs: list[Hub], target_hub: Hub) -> dict[Hub, float]:
    distances: dict[Hub, float] = {hub: inf for hub in hubs}
    distances[target_hub] = 0.0

    queue: list[tuple[float, int, Hub]] = []
    tie_breaker = count()
    heappush(queue, (0.0, next(tie_breaker), target_hub))

    while queue:
        current_distance, _, current_hub = heappop(queue)
        if current_distance > distances[current_hub]:
            continue

        if current_hub.zone == "blocked":
            continue

        for edge in graph.nodes.get(current_hub, []):
            next_hub = edge.target
            if next_hub.zone == "blocked":
                continue

            new_distance = current_distance + next_hub.cost
            if new_distance < distances[next_hub]:
                distances[next_hub] = new_distance
                heappush(queue, (new_distance, next(tie_breaker), next_hub))

    return distances


def get_connection_label(
    connection_labels: dict[frozenset[str], str],
    source_hub: Hub,
    destination_hub: Hub,
) -> str:
    key = frozenset((source_hub.name, destination_hub.name))
    return connection_labels.get(key, f"{source_hub.name}-{destination_hub.name}")


def hub_midpoint(hub1: Hub, hub2: Hub) -> tuple[float, float]:
    return (
        (hub1.position_on_window[0] + hub2.position_on_window[0]) / 2,
        (hub1.position_on_window[1] + hub2.position_on_window[1]) / 2,
    )


def lerp_position(start: tuple[float, float], end: tuple[float, float], progress: float) -> tuple[float, float]:
    return (
        start[0] + (end[0] - start[0]) * progress,
        start[1] + (end[1] - start[1]) * progress,
    )


def rank_next_hubs(
    graph: Graph,
    current_hub: Hub,
    start_hub: Hub,
    target_hub: Hub,
    static_distances: dict[Hub, float],
    drone: Drone,
):
    ranked_candidates: list[tuple[float, float, float, Hub]] = []
    current_distance = static_distances.get(current_hub, inf)
    if current_distance == inf:
        return ranked_candidates

    for edge in graph.nodes.get(current_hub, []):
        next_hub = edge.target
        next_distance = static_distances.get(next_hub, inf)
        if next_distance == inf:
            continue
        if next_hub.zone == "blocked":
            continue
        if not graph.edge_available(current_hub, next_hub):
            continue
        if not can_enter_hub(next_hub, start_hub, target_hub):
            continue

        if next_distance > current_distance:
            continue

        forward_options = sum(
            1
            for next_edge in graph.nodes.get(next_hub, [])
            if static_distances.get(next_edge.target, inf) < next_distance
        )
        if next_hub != target_hub and forward_options == 0:
            continue

        revisit_penalty = 0.0
        if next_hub in drone.passed_hubs:
            revisit_penalty += 12.0
        if len(drone.passed_hubs) >= 2 and next_hub == drone.passed_hubs[-2]:
            revisit_penalty += 25.0
        ranked_candidates.append((next_distance, revisit_penalty, -float(forward_options), next_hub))

    ranked_candidates.sort(key=lambda item: (item[0], item[1], item[2], item[3].name))
    return ranked_candidates


def draw_scene(window, connections, hubs, start_hub, target_hub, drones, turn_text, write_text):
    window.fill(colors["background"])
    draw_connections(window, connections, hubs)
    draw_hubs(window, hubs)
    draw_flags(window, start_hub, target_hub)
    write_text(window, turn_text)
    for drone in drones:
        drone.show(window, drone.display_position[0], drone.display_position[1])
    pygame.display.update()


def animate_movements(
    window,
    clock,
    connections,
    hubs,
    start_hub,
    target_hub,
    drones,
    write_text,
    turn_text,
    movements,
    frames: int = 12,
):
    if not movements:
        draw_scene(window, connections, hubs, start_hub, target_hub, drones, turn_text, write_text)
        clock.tick(6)
        return True

    for frame in range(1, frames + 1):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

        progress = frame / frames
        for drone, start_position, end_position in movements:
            drone.display_position = lerp_position(start_position, end_position, progress)

        draw_scene(window, connections, hubs, start_hub, target_hub, drones, turn_text, write_text)
        clock.tick(24)

    for drone, _, end_position in movements:
        drone.display_position = end_position

    return True


def main():
    pygame.init()

    font = pygame.font.SysFont(None, 32)

    def write_text(window, txt: str):
        text_surface = font.render(txt, True, (255, 255, 255))
        window.blit(text_surface, (50, 100))

    hubs: list[Hub] = []
    connections: list[tuple[str, str, int, str]] = []
    nb_drones = 0
    start_hub: Hub | None = None
    target_hub: Hub | None = None

    try:
        file_path = sys.argv[1]
        with open(file_path, "r", encoding="utf-8") as map_file_handle:
            map_file = map_file_handle.readlines()
    except (IOError, IndexError) as error:
        print(f"error : {error}")
        sys.exit(0)

    for line in map_file:
        if line.startswith("#"):
            continue

        if line.startswith("nb_drones"):
            nb_drones = int(line.split()[1])
            continue

        if (
            line.startswith("start_hub")
            or line.startswith("hub")
            or line.startswith("end_hub")
        ):
            data = line.split()
            meta_data_dict = parse_metadata(line)
            hub = Hub(
                name=data[1],
                x=int(data[2]),
                y=int(data[3]),
                color=meta_data_dict.get("color", "none"),
                zone=meta_data_dict.get("zone", "normal"),
                max_drones=meta_data_dict.get("max_drones", 1),
            )
            hubs.append(hub)
            if line.startswith("start_hub"):
                start_hub = hub
            elif line.startswith("end_hub"):
                target_hub = hub
            continue

        if line.startswith("connection"):
            connections.append(parse_connection(line))

    if nb_drones <= 0 or not hubs or start_hub is None or target_hub is None:
        print("error : invalid map file")
        sys.exit(0)

    avg_x = sum(hub.x for hub in hubs) / len(hubs)
    avg_y = sum(hub.y for hub in hubs) / len(hubs)

    graph = Graph()
    init_the_graph(graph, hubs, connections)
    connection_labels = build_connection_labels(connections)
    static_distances = build_static_distance_map(graph, hubs, target_hub)
    cost_func = make_cost_func(start_hub, target_hub)

    width, height = 1700, 1000
    for hub in hubs:
        x = width // 2 + (hub.x - avg_x) * 60
        y = height // 2 + (hub.y - avg_y) * 160
        hub.position_on_window = (x, y)

    window = pygame.display.set_mode((width, height))
    window.fill(colors["background"])
    pygame.display.set_caption("Fly-In")

    drones: list[Drone] = [Drone(start_hub, target_hub, index + 1) for index in range(nb_drones)]
    start_hub.corrent_number_of_drones = nb_drones

    turn = 0
    clock = pygame.time.Clock()
    turn_print = 1
    run = True

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        turn += 1
        turn_events: list[str] = []
        turn_movements: list[tuple[Drone, tuple[float, float], tuple[float, float]]] = []
        turn_reservations: list[tuple[Hub, Hub]] = []
        arrived_this_turn: set[int] = set()

        for drone in drones:
            if not drone.in_transit:
                continue

            drone.turns_remaining -= 1
            if drone.turns_remaining > 0:
                continue

            if drone.active_edge is not None:
                graph.release_edge(*drone.active_edge)
                drone.active_edge = None

            arrival_hub = drone.current_target
            if arrival_hub is None:
                drone.in_transit = False
                drone.turns_remaining = 0
                continue

            drone.corrent_hub = arrival_hub
            drone.corrent_position = arrival_hub.position_on_window
            arrival_start = drone.display_position
            arrival_end = arrival_hub.position_on_window
            drone.display_position = arrival_start
            drone.current_target = arrival_hub
            drone.in_transit = False
            drone.turns_remaining = 0
            drone.transit_connection_name = None
            drone.passed_hubs.append(arrival_hub)
            turn_events.append(f"D{drone.identifier}-{arrival_hub.name}")
            turn_movements.append((drone, arrival_start, arrival_end))
            arrived_this_turn.add(drone.identifier)

            if arrival_hub == target_hub:
                drone.reach_target = True

        for drone in drones:
            if drone.reach_target or drone.in_transit or drone.identifier in arrived_this_turn:
                continue

            drone.set_path(graph, cost_func)
            ranked_candidates = rank_next_hubs(graph, drone.corrent_hub, start_hub, target_hub, static_distances, drone)
            if not ranked_candidates:
                continue

            next_hub = None
            for _, _, _, candidate_hub in ranked_candidates[:3]:
                if candidate_hub == drone.corrent_hub:
                    continue
                next_hub = candidate_hub
                break

            if next_hub is None:
                continue

            source_hub = drone.corrent_hub
            connection_name = get_connection_label(connection_labels, source_hub, next_hub)
            graph.reserve_edge(source_hub, next_hub)
            source_hub.corrent_number_of_drones -= 1
            start_position = source_hub.position_on_window

            if next_hub.zone == "restricted":
                next_hub.corrent_number_of_drones += 1
                drone.active_edge = (source_hub, next_hub)
                drone.in_transit = True
                drone.turns_remaining = 1
                drone.current_target = next_hub
                drone.transit_connection_name = connection_name
                drone.display_position = start_position
                turn_events.append(f"D{drone.identifier}-{connection_name}")
                turn_movements.append((drone, start_position, hub_midpoint(source_hub, next_hub)))
            else:
                next_hub.corrent_number_of_drones += 1
                drone.corrent_hub = next_hub
                drone.corrent_position = next_hub.position_on_window
                drone.display_position = start_position
                drone.current_target = next_hub
                drone.passed_hubs.append(next_hub)
                turn_events.append(f"D{drone.identifier}-{next_hub.name}")
                if next_hub == target_hub:
                    drone.reach_target = True
                turn_reservations.append((source_hub, next_hub))
                turn_movements.append((drone, start_position, next_hub.position_on_window))

        for source_hub, destination_hub in turn_reservations:
            graph.release_edge(source_hub, destination_hub)

        print(turn_print , " ".join(turn_events), flush=True)
        turn_print += 1

        if turn_events and any(drone.in_transit for drone in drones):
            turn += 1

        if not animate_movements(
            window,
            clock,
            connections,
            hubs,
            start_hub,
            target_hub,
            drones,
            write_text,
            f"turn = {turn}",
            turn_movements,
        ):
            run = False
            # break
        sleep(0.003)

    pygame.quit()

if __name__ == "__main__":
    main()