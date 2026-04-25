from __future__ import annotations

from math import inf


class Hub:
    def __init__(self, name: str, x: int, y: int, color: str = "none", zone: str = "normal", max_drones: int = 1):
        self.name = name
        self.x = x
        self.y = y
        self.color = color
        self.zone = zone
        self.max_drones = int(max_drones)
        self.position_on_window: tuple[float, float] = (-1.0, -1.0)
        self.current_drones = 0
        self.cost = self.zone_cost(zone)

    @staticmethod
    def zone_cost(zone: str) -> float:
        if zone == "blocked":
            return inf
        if zone == "priority":
            return 0.5
        if zone == "restricted":
            return 2.0
        return 1.0

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Hub) and self.name == other.name

    def __lt__(self, other: Hub) -> bool:
        return (self.cost, self.name) < (other.cost, other.name)

    def __repr__(self) -> str:
        return self.name

    @staticmethod
    def get_hub(name: str, hubs: list[Hub]) -> Hub | None:
        for hub in hubs:
            if hub.name == name:
                return hub
        return None

    @staticmethod
    def can_enter_hub(hub: Hub, start_hub: Hub, target_hub: Hub) -> bool:
        if hub in (start_hub, target_hub):
            return True
        if hub.zone == "blocked":
            return False
        return hub.current_drones < hub.max_drones


class Edge:
    def __init__(self, target: Hub, capacity: int = 1):
        self.target = target
        self.capacity = int(capacity)
        self.cost = self.target.cost

    def __repr__(self) -> str:
        return f"cost={self.cost} target={self.target} capacity={self.capacity}"


class Drone:
    def __init__(self, identifier: int, start_hub: Hub, target_hub: Hub):
        self.id = identifier
        self.start_hub = start_hub
        self.target_hub = target_hub
        self.current_hub = start_hub
        self.display_position = start_hub.position_on_window
        self.current_position = start_hub.position_on_window
        self.passed_hubs: list[Hub] = [start_hub]
        self.reached = False
        self.in_transit = False
        self.turns_remaining = 0
        self.transit_source: Hub | None = None
        self.transit_destination: Hub | None = None
        self.active_edge: tuple[Hub, Hub] | None = None

    def __repr__(self) -> str:
        return f"Drone({self.id})"


class Graph:
    def __init__(self):
        self.nodes: dict[Hub, list[Edge]] = {}
        self.link_capacity: dict[tuple[str, str], int] = {}
        self.link_load: dict[tuple[str, str], int] = {}

    def edge_key(self, hub1: Hub, hub2: Hub) -> tuple[str, str]:
        return hub1.name, hub2.name

    def add_link(self, hub1: Hub, hub2: Hub, capacity: int = 1) -> None:
        key = self.edge_key(hub1, hub2)
        self.link_capacity[key] = int(capacity)
        self.link_load.setdefault(key, 0)

    def add_edge(self, hub1: Hub, hub2: Hub, capacity: int = 1) -> None:
        self.add_link(hub1, hub2, capacity)
        self.nodes.setdefault(hub1, [])
        if all(edge.target != hub2 for edge in self.nodes[hub1]):
            self.nodes[hub1].append(Edge(hub2, capacity))

    def build_from_connections(self, hubs: list[Hub], connections: list[tuple[str, str, int]]) -> None:
        hub_by_name = {hub.name: hub for hub in hubs}
        for first_name, second_name, capacity in connections:
            hub1 = hub_by_name.get(first_name)
            hub2 = hub_by_name.get(second_name)
            if hub1 is None or hub2 is None:
                continue
            self.add_edge(hub1, hub2, capacity)
            self.add_edge(hub2, hub1, capacity)

    def edge_capacity(self, hub1: Hub, hub2: Hub) -> int:
        return self.link_capacity.get(self.edge_key(hub1, hub2), 1)

    def edge_load(self, hub1: Hub, hub2: Hub) -> int:
        return self.link_load.get(self.edge_key(hub1, hub2), 0)

    def edge_available(self, hub1: Hub, hub2: Hub) -> bool:
        return self.edge_load(hub1, hub2) < self.edge_capacity(hub1, hub2)

    def reserve_edge(self, hub1: Hub, hub2: Hub) -> None:
        key = self.edge_key(hub1, hub2)
        self.link_load[key] = self.link_load.get(key, 0) + 1

    def release_edge(self, hub1: Hub, hub2: Hub) -> None:
        key = self.edge_key(hub1, hub2)
        self.link_load[key] = max(0, self.link_load.get(key, 0) - 1)