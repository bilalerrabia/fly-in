"""Score-based routing heuristic for drone movement.

The planner keeps a shortest-distance map to the target and then scores each
hub dynamically based on:
- whether the hub can still reach the target,
- how far it is from the target,
- how many forward options it keeps open,
- how crowded it currently is,
- and whether it is a priority or restricted zone.

This is a routing helper, not a proof of optimality. It is designed to keep
drones on the shortest feasible route while respecting hub and link capacity.
"""

from __future__ import annotations

from dataclasses import dataclass
from heapq import heappop, heappush
from itertools import count
from math import inf
from typing import Callable

from classes import Drone, Graph, Hub

CostFunc = Callable[[Hub], float]

_ZONE_BONUS = {
    "priority": 8.0,
    "normal": 0.0,
    "restricted": -8.0,
    "blocked": -1000.0,
}


@dataclass(frozen=True)
class HubScore:
    reachable: bool
    distance_to_target: float
    forward_options: int
    total_options: int
    free_capacity: int
    occupancy_ratio: float
    score: float


class ScoreBasedRouter:
    def __init__(self, graph: Graph, target_hub: Hub, cost_func: CostFunc | None = None, score_margin: float = 0.0):
        self.graph = graph
        self.target_hub = target_hub
        self.cost_func = cost_func or (lambda hub: hub.cost)
        self.score_margin = score_margin
        self.distance_to_target: dict[Hub, float] = {}
        self.hub_scores: dict[Hub, HubScore] = {}
        self.rebuild()

    def _all_hubs(self) -> set[Hub]:
        hubs: set[Hub] = {self.target_hub}
        for hub, edges in self.graph.nodes.items():
            hubs.add(hub)
            for edge in edges:
                hubs.add(edge.target)
        return hubs

    def _build_distance_map(self) -> dict[Hub, float]:
        distances = {hub: inf for hub in self._all_hubs()}
        distances[self.target_hub] = 0.0

        queue: list[tuple[float, int, Hub]] = []
        tie_breaker = count()
        heappush(queue, (0.0, next(tie_breaker), self.target_hub))

        while queue:
            current_cost, _, current_hub = heappop(queue)
            if current_cost > distances[current_hub]:
                continue

            enter_cost = self.cost_func(current_hub)
            if enter_cost == inf:
                continue

            for edge in self.graph.nodes.get(current_hub, []):
                next_hub = edge.target
                new_cost = current_cost + enter_cost
                if new_cost < distances[next_hub]:
                    distances[next_hub] = new_cost
                    heappush(queue, (new_cost, next(tie_breaker), next_hub))

        return distances

    def _count_local_escape_options(self, hub: Hub) -> int:
        escape_options = 0
        for edge in self.graph.nodes.get(hub, []):
            next_hub = edge.target
            if next_hub.zone == "blocked":
                continue
            if not self.graph.edge_available(hub, next_hub):
                continue
            if next_hub.corrent_number_of_drones >= next_hub.max_drones and next_hub != self.target_hub:
                continue
            escape_options += 1
        return escape_options

    def _build_hub_score(self, hub: Hub) -> HubScore:
        distance = self.distance_to_target.get(hub, inf)
        if distance == inf or hub.zone == "blocked":
            return HubScore(
                reachable=False,
                distance_to_target=inf,
                forward_options=0,
                total_options=0,
                free_capacity=0,
                occupancy_ratio=1.0,
                score=float("-inf"),
            )

        neighbors = self.graph.nodes.get(hub, [])
        total_options = len(neighbors)
        forward_options = sum(
            1
            for edge in neighbors
            if self.distance_to_target.get(edge.target, inf) < distance
        )
        free_capacity = max(0, hub.max_drones - hub.corrent_number_of_drones)
        occupancy_ratio = hub.corrent_number_of_drones / max(1, hub.max_drones)

        closeness_score = 100.0 / (1.0 + distance)
        branching_score = 12.0 * forward_options
        capacity_score = 18.0 * (free_capacity / max(1, hub.max_drones))
        crowding_penalty = 20.0 * occupancy_ratio
        zone_bonus = _ZONE_BONUS.get(hub.zone, 0.0)
        dead_end_penalty = 15.0 if forward_options == 0 and hub != self.target_hub else 0.0

        score = (
            closeness_score
            + branching_score
            + capacity_score
            + zone_bonus
            - crowding_penalty
            - dead_end_penalty
        )

        if hub == self.target_hub:
            score += 25.0

        return HubScore(
            reachable=True,
            distance_to_target=distance,
            forward_options=forward_options,
            total_options=total_options,
            free_capacity=free_capacity,
            occupancy_ratio=occupancy_ratio,
            score=score,
        )

    def rebuild(self) -> None:
        self.distance_to_target = self._build_distance_map()
        self.refresh_scores()

    def refresh_scores(self) -> None:
        self.hub_scores = {hub: self._build_hub_score(hub) for hub in self._all_hubs()}

    def ranked_hubs(self) -> list[tuple[Hub, HubScore]]:
        return sorted(
            self.hub_scores.items(),
            key=lambda item: item[1].score,
            reverse=True,
        )

    def choose_next_hub(self, drone: Drone) -> Hub | None:
        current_hub = drone.corrent_hub
        current_distance = self.distance_to_target.get(current_hub, inf)
        if current_distance == inf or current_hub == self.target_hub:
            return None

        candidates: list[tuple[float, float, float, int, Hub]] = []
        for edge in self.graph.nodes.get(current_hub, []):
            next_hub = edge.target
            next_distance = self.distance_to_target.get(next_hub, inf)
            if next_distance == inf:
                continue
            if next_hub != self.target_hub and next_hub.corrent_number_of_drones >= next_hub.max_drones:
                continue
            if not self.graph.edge_available(current_hub, next_hub):
                continue

            next_score = self.hub_scores.get(next_hub)
            if next_score is None or next_score.score == float("-inf"):
                continue

            branch_bonus = float(next_score.forward_options)
            candidate_score = next_score.score + branch_bonus
            candidates.append(
                (
                    next_distance,
                    candidate_score,
                    -next_score.free_capacity,
                    -edge.cost,
                    next_hub,
                )
            )

        if not candidates:
            return None

        best_distance = min(candidate[0] for candidate in candidates)
        if best_distance >= current_distance:
            return None

        best_candidates = [candidate for candidate in candidates if candidate[0] == best_distance]
        if not best_candidates:
            return None

        best_candidate = max(
            best_candidates,
            key=lambda candidate: (
                candidate[1],
                candidate[2],
                candidate[3],
            ),
        )
        return best_candidate[4]

    def launch_drone(self, drone: Drone) -> Hub | None:
        next_hub = self.choose_next_hub(drone)
        if next_hub is None:
            return None

        self.graph.reserve_edge(drone.corrent_hub, next_hub)
        drone.corrent_hub.corrent_number_of_drones -= 1
        next_hub.corrent_number_of_drones += 1
        drone.active_edge = (drone.corrent_hub, next_hub)
        drone.current_target = next_hub
        drone.in_transit = True
        return next_hub

    def finish_drone_move(self, drone: Drone) -> None:
        if drone.active_edge is not None:
            self.graph.release_edge(*drone.active_edge)
            drone.active_edge = None

        drone.corrent_hub = drone.current_target
        drone.corrent_position = drone.current_target.position_on_window
        drone.in_transit = False
        if drone.corrent_hub == self.target_hub:
            drone.reach_target = True
