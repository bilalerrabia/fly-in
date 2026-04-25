import sys
import pygame
from heapq import heappop, heappush
from itertools import count
from math import inf
from time import sleep

from some_parameters import colors
from classes import Hub, Graph, Edge, Drone, Drawing_Animation_Methods
from dijkstra import djikstra
from draw_flags import draw_flags
from parsing import parsing


def build_static_distance_map(graph: Graph, hubs: list[Hub], target_hub: Hub) -> dict[Hub, float]:
    distances: dict[Hub, float] = {hub: inf for hub in hubs}
    distances[target_hub] = 0.0

    queue: list[tuple[float, Hub]] = []
    heappush(queue, (0.0, target_hub))

    while queue:
        current_distance, current_hub = heappop(queue)
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
                heappush(queue, (new_distance, next_hub))

    return distances


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
        if not Hub.can_enter_hub(next_hub, start_hub, target_hub):
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

    hubs, connections, start_hub, target_hub, nb_drones = parsing(hubs, connections, start_hub, target_hub)

    if nb_drones <= 0 or not hubs or start_hub is None or target_hub is None:
        print("error : invalid map file")
        sys.exit(0)

    avg_x = sum(hub.x for hub in hubs) / len(hubs)
    avg_y = sum(hub.y for hub in hubs) / len(hubs)

    graph = Graph()
    Graph.init_the_graph(graph, hubs, connections)
    # connection_labels = build_connection_labels(connections)
    static_distances = build_static_distance_map(graph, hubs, target_hub)
    # cost_func = make_cost_func(start_hub, target_hub)

    width, height = 1700, 1000
    for hub in hubs:
        x = width // 2 + (hub.x - avg_x) * 60
        y = height // 2 + (hub.y - avg_y) * 160
        hub.position_on_window = (x, y)

    window = pygame.display.set_mode((width, height))
    window.fill(colors["background"])
    pygame.display.set_caption("fly-in okda ajmi chkt3rf")

    drones: list[Drone] = [Drone(start_hub, target_hub, index + 1) for index in range(nb_drones)]
    start_hub.corrent_number_of_drones = nb_drones

    turn = 0
    clock = pygame.time.Clock()
    # turn_print = 1
    run = True

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False


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

            if drone.active_edge :
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

            # drone.set_path(graph)
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
            connection_name = f"{source_hub.name}-{next_hub.name}"
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
                turn_movements.append((drone, start_position, Drawing_Animation_Methods.lerp_position(start_position, next_hub.position_on_window, 0.5)))
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

        if turn_events:
            turn += 1
            print(turn , " ".join(turn_events))

        Drawing_Animation_Methods.animate_movements(window, clock, connections, hubs, start_hub,
            target_hub, drones, write_text, f"turn = {turn}", turn_movements)

    pygame.quit()

if __name__ == "__main__":
    main()
