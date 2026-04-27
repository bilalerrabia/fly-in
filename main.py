# import sys
import pygame
from heapq import heappop, heappush
from math import inf
# from time import sleep

from some_parameters import colors
from classes import Hub, Graph, Drone
from render import Rendring
from parsing import parsing


def build_static_distance_map(
        graph: Graph,
        target_hub: Hub) -> dict[Hub, float]:
    distances: dict[Hub, float] = {target_hub: 0.0}

    queue: list[tuple[float, Hub]] = []
    heappush(queue, (0.0, target_hub))

    while queue:
        distance, hub = heappop(queue)
        if distance > distances.get(hub, inf):
            continue

        if hub.zone == "blocked":
            continue

        for edge in graph.nodes.get(hub, []):
            neighbor = edge.target
            if neighbor.zone == "blocked":
                continue

            new_distance = distance + neighbor.cost
            if new_distance < distances.get(neighbor, inf):
                distances[neighbor] = new_distance
                heappush(queue, (new_distance, neighbor))

    return distances


def rank_next_hubs(
    graph: Graph,
    current_hub: Hub,
    target_hub: Hub,
    static_distances: dict[Hub, float],
) -> list[Hub]:
    current_distance = static_distances.get(current_hub, inf)
    if current_distance == inf:
        return []

    ranked_candidates: list[tuple[float, bool, Hub]] = []
    for edge in graph.nodes.get(current_hub, []):
        next_hub = edge.target
        next_distance = static_distances.get(next_hub, inf)
        if (
            next_distance == inf or
            next_distance > current_distance or
            not next_hub.can_enter_hub()
        ):
            continue

        has_forward_path = any(
            static_distances.get(next_edge.target, inf) < next_distance
            for next_edge in graph.nodes.get(next_hub, [])
        )
        if next_hub != target_hub and not has_forward_path:
            continue

        ranked_candidates.append(
            (
                next_distance,
                not has_forward_path, next_hub
            ))

    ranked_candidates.sort(key=lambda item: (item[0], item[1], item[2].name))
    return [hub for _, _, hub in ranked_candidates]


def main() -> None:

    pygame.init()

    font = pygame.font.SysFont("test", 32)

    def write_text(window: pygame.Surface, txt: str) -> None:
        """Render a single status line on the top left window."""
        text_surface = font.render(txt, True, (255, 255, 255))
        window.blit(text_surface, (50, 100))

    hubs, connections, start_hub, target_hub, nb_drones = parsing()

    graph = Graph(hubs, connections)
    static_distances = build_static_distance_map(graph, target_hub)

    # init the hub.position_on_window
    avg_x = sum(hub.x for hub in hubs) / len(hubs)
    avg_y = sum(hub.y for hub in hubs) / len(hubs)
    width, height = 1700, 1000
    for hub in hubs:
        x = width // 2 + (hub.x - avg_x) * 60
        y = height // 2 + (hub.y - avg_y) * 160
        hub.position_on_window = (x, y)

    # init the pygame window
    window = pygame.display.set_mode((width, height))
    window.fill(colors["background"])
    pygame.display.set_caption("fly-in okda ajmi chkt3rf")

    drones: list[Drone] = [
        Drone(start_hub, target_hub, index + 1)
        for index in range(nb_drones)
        ]
    start_hub.corrent_number_of_drones = nb_drones

    clock = pygame.time.Clock()

    turn = 0
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        turn_events: list[str] = []
        turn_movements: list[tuple[Drone, tuple, tuple]] = []
        turn_reservations: list[tuple[Hub, Hub]] = []
        arrived_this_turn: set[int] = set()

        for drone in drones:
            if not drone.in_transit:
                continue

            arrival_hub = drone.current_target
            if arrival_hub is None:
                drone.in_transit = False
                continue

            arrival_start = drone.corrent_position
            arrival_end = arrival_hub.position_on_window
            drone.corrent_hub = arrival_hub
            drone.corrent_position = arrival_end
            drone.current_target = arrival_hub
            drone.in_transit = False
            turn_events.append(f"D{drone.id}-{arrival_hub.name}")
            turn_movements.append((drone, arrival_start, arrival_end))
            arrived_this_turn.add(drone.id)

            if arrival_hub == target_hub:
                drone.reach_target = True

        for drone in drones:
            if (
                drone.reach_target or
                drone.in_transit or
                drone.id in arrived_this_turn
            ):
                continue
            ranked_candidates = rank_next_hubs(
                graph, drone.corrent_hub, target_hub, static_distances)
            if not ranked_candidates:
                continue

            next_hub = next(
                (
                    candidate_hub
                    for candidate_hub in ranked_candidates[:3]
                    if candidate_hub != drone.corrent_hub), None)

            if next_hub is None:
                continue

            source_hub = drone.corrent_hub
            connection_name = f"{source_hub.name}-{next_hub.name}"
            source_hub.corrent_number_of_drones -= 1
            start_position = source_hub.position_on_window

            if next_hub.zone == "restricted":
                next_hub.corrent_number_of_drones += 1
                drone.in_transit = True
                drone.current_target = next_hub
                drone.corrent_position = start_position
                turn_events.append(f"D{drone.id}-{connection_name}")
                turn_movements.append(
                    (drone, start_position, next_hub.position_on_window))
            else:
                next_hub.corrent_number_of_drones += 1
                drone.corrent_hub = next_hub
                drone.corrent_position = next_hub.position_on_window
                drone.corrent_position = start_position
                drone.current_target = next_hub
                turn_events.append(f"D{drone.id}-{next_hub.name}")
                if next_hub == target_hub:
                    drone.reach_target = True
                turn_reservations.append((source_hub, next_hub))
                turn_movements.append(
                    (drone, start_position, next_hub.position_on_window))

        if turn_events:
            turn += 1
            print(turn, " ".join(turn_events))
        Rendring.draw_turn(
            window, clock, connections, hubs, start_hub,
            target_hub, drones, write_text, f"turn = {turn}", turn_movements)

    pygame.quit()


if __name__ == "__main__":
    main()
