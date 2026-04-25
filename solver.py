from __future__ import annotations

from heapq import heappop, heappush
from itertools import count
from math import inf

from model import Drone, Graph, Hub


class TurnResult:
    def __init__(self, events: list[str], movements: list[tuple[Drone, tuple[float, float], tuple[float, float]]]):
        self.events = events
        self.movements = movements


def build_distance_map(graph: Graph, target_hub: Hub) -> dict[Hub, float]:
    distances: dict[Hub, float] = {hub: inf for hub in graph.nodes}
    distances[target_hub] = 0.0

    queue: list[tuple[float, int, Hub]] = []
    tie_breaker = count()
    heappush(queue, (0.0, next(tie_breaker), target_hub))

    while queue:
        current_distance, _, current_hub = heappop(queue)
        if current_distance > distances.get(current_hub, inf):
            continue
        if current_hub.zone == "blocked":
            continue

        for edge in graph.nodes.get(current_hub, []):
            next_hub = edge.target
            if next_hub.zone == "blocked":
                continue

            new_distance = current_distance + next_hub.cost
            if new_distance < distances.get(next_hub, inf):
                distances[next_hub] = new_distance
                heappush(queue, (new_distance, next(tie_breaker), next_hub))

    return distances


def rank_next_hubs(
    graph: Graph,
    current_hub: Hub,
    start_hub: Hub,
    target_hub: Hub,
    distance_map: dict[Hub, float],
    drone: Drone,
) -> list[tuple[float, float, float, Hub]]:
    current_distance = distance_map.get(current_hub, inf)
    if current_distance == inf:
        return []

    ranked: list[tuple[float, float, float, Hub]] = []
    for edge in graph.nodes.get(current_hub, []):
        next_hub = edge.target
        next_distance = distance_map.get(next_hub, inf)
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
            if distance_map.get(next_edge.target, inf) < next_distance
        )
        if next_hub != target_hub and forward_options == 0:
            continue

        revisit_penalty = 0.0
        if next_hub in drone.passed_hubs:
            revisit_penalty += 12.0
        if len(drone.passed_hubs) >= 2 and next_hub == drone.passed_hubs[-2]:
            revisit_penalty += 25.0

        ranked.append((next_distance, revisit_penalty, -float(forward_options), next_hub))

    ranked.sort(key=lambda item: (item[0], item[1], item[2], item[3].name))
    return ranked


def choose_next_hub(
    graph: Graph,
    drone: Drone,
    start_hub: Hub,
    target_hub: Hub,
    distance_map: dict[Hub, float],
) -> Hub | None:
    ranked_candidates = rank_next_hubs(
        graph,
        drone.current_hub,
        start_hub,
        target_hub,
        distance_map,
        drone,
    )
    for _, _, _, candidate in ranked_candidates[:3]:
        if candidate != drone.current_hub:
            return candidate
    return None


def advance_turn(
    drones: list[Drone],
    graph: Graph,
    start_hub: Hub,
    target_hub: Hub,
    distance_map: dict[Hub, float],
) -> TurnResult:
    events: list[str] = []
    movements: list[tuple[Drone, tuple[float, float], tuple[float, float]]] = []
    normal_reservations: list[tuple[Hub, Hub]] = []
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

        destination = drone.transit_destination
        if destination is None:
            drone.in_transit = False
            drone.turns_remaining = 0
            continue

        start_position = drone.display_position
        end_position = destination.position_on_window
        drone.current_hub = destination
        drone.current_position = destination.position_on_window
        drone.display_position = start_position
        drone.in_transit = False
        drone.turns_remaining = 0
        drone.transit_source = None
        drone.transit_destination = None
        drone.passed_hubs.append(destination)
        drone.reached = drone.reached or destination == target_hub

        events.append(f"D{drone.id}-{destination.name}")
        movements.append((drone, start_position, end_position))
        arrived_this_turn.add(drone.id)

    for drone in drones:
        if drone.reached or drone.in_transit or drone.id in arrived_this_turn:
            continue

        next_hub = choose_next_hub(graph, drone, start_hub, target_hub, distance_map)
        if next_hub is None:
            continue

        source_hub = drone.current_hub
        start_position = source_hub.position_on_window
        graph.reserve_edge(source_hub, next_hub)
        source_hub.current_drones -= 1

        if next_hub.zone == "restricted":
            next_hub.current_drones += 1
            drone.in_transit = True
            drone.turns_remaining = 1
            drone.transit_source = source_hub
            drone.transit_destination = next_hub
            drone.active_edge = (source_hub, next_hub)
            drone.display_position = start_position
            events.append(f"D{drone.id}-{source_hub.name}-{next_hub.name}")
            midpoint = (
                start_position[0] + (next_hub.position_on_window[0] - start_position[0]) * 0.5,
                start_position[1] + (next_hub.position_on_window[1] - start_position[1]) * 0.5,
            )
            movements.append((drone, start_position, midpoint))
        else:
            next_hub.current_drones += 1
            drone.current_hub = next_hub
            drone.current_position = next_hub.position_on_window
            drone.display_position = start_position
            drone.passed_hubs.append(next_hub)
            drone.reached = drone.reached or next_hub == target_hub
            events.append(f"D{drone.id}-{next_hub.name}")
            movements.append((drone, start_position, next_hub.position_on_window))
            normal_reservations.append((source_hub, next_hub))

    for source_hub, destination_hub in normal_reservations:
        graph.release_edge(source_hub, destination_hub)

    return TurnResult(events=events, movements=movements)
