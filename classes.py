"""Core graph, hub, edge, and drone models used by the simulation."""

from __future__ import annotations

import pygame
import os
import random
from math import inf


class Hub:
    """Represent a hub in the map graph and track its live occupancy."""

    def __init__(
            self, name: str, x: int, y: int,
            color: str, zone: str, max_drones: int):
        """Create a hub with its coordinates, zone, and capacity."""
        self.name = name
        self.x = x
        self.y = y
        self.color = color
        self.zone = zone
        self.max_drones = int(max_drones)
        self.position_on_window: tuple[float, float] = (-1, -1)
        self.cost: float = self.get_cost(self.zone)
        self.corrent_number_of_drones = 0

    @staticmethod
    def get_cost(zone: str) -> float:
        """Map a zone name to its traversal cost."""
        return {
            "blocked": inf,
            "priority": 0.5,
            "normal": 1,
            "restricted": 2,
        }.get(zone, inf)

    @staticmethod
    def get_hub(name: str, hubs: list[Hub]) -> Hub | None:
        """Return the hub with the requested name, if it exists."""
        return next((hub for hub in hubs if hub.name == name), None)

    def can_enter_hub(self) -> bool:
        """Return True when the hub is open and has spare capacity."""
        return (
            self.zone != "blocked" and
            self.corrent_number_of_drones < self.max_drones)

    def __lt__(self, other: Hub) -> bool:
        """Order hubs by traversal cost for heap operations."""
        return self.cost < other.cost

    def __repr__(self) -> str:
        """Return the hub name for debugging output."""
        return self.name


class Graph:
    """Build an undirected adjacency map from the declared connections."""

    def __init__(
            self, hubs: list[Hub],
            connections: list[tuple[str, str, int]]) -> None:
        """Create graph edges for every connection in both directions."""
        self.nodes: dict[Hub, list[Edge]] = {}
        for connection in connections:
            hub1 = Hub.get_hub(connection[0], hubs)
            hub2 = Hub.get_hub(connection[1], hubs)
            Edge.add_edge(self, hub1, hub2)
            Edge.add_edge(self, hub2, hub1)

    def __repr__(self) -> str:
        """Render the adjacency list for debugging."""
        rep = ""
        for key, value in self.nodes.items():
            rep += f"{key} = {value}\n"
        return rep


class Edge:
    """Store a weighted edge to a neighboring hub."""

    def __init__(self, cost: float, target: Hub) -> None:
        """Create an edge to a target hub with the target's traversal cost."""
        self.cost: float = cost
        self.target: Hub = target

    @staticmethod
    def is_there(name: str, list_edges: list[Edge]) -> bool:
        """Return True when the neighbor list already contains the hub."""
        return any(name == edge.target.name for edge in list_edges)

    @staticmethod
    def add_edge(graph: Graph, hub1: Hub | None, hub2: Hub | None) -> None:
        """Add a directed edge if both hubs exist and the edge is new."""
        if hub1 is None or hub2 is None:
            return

        neighbors = graph.nodes.setdefault(hub1, [])
        if not Edge.is_there(hub2.name, neighbors):
            neighbors.append(Edge(hub2.cost, hub2))

    def __repr__(self) -> str:
        """Return a compact debugging representation of the edge."""
        return f"cost={self.cost} target={self.target}"


class Drone:
    """Represent one simulated drone and its current animation state."""

    def __init__(self, start_hub: Hub, drone_id: int):
        """Load a drone sprite and place the drone at the start hub."""
        img_path = f"photos/{random.choice(os.listdir('photos'))}"
        self.img = pygame.transform.scale(
            pygame.image.load(img_path), (70, 70))
        self.id = drone_id
        self.corrent_hub: Hub = start_hub
        self.corrent_position: tuple[float, float] = (0, 0)
        self.corrent_position = start_hub.position_on_window
        self.current_target: Hub | None = None
        self.reach_final_target: bool = False
        self.in_transit: bool = False

    def show(
            self, window: pygame.surface.Surface,
            img_x: float, img_y: float) -> None:
        """Draw the drone sprite centered on the provided coordinates."""
        window.blit(self.img, (img_x - 30, img_y - 30))
