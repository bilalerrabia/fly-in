import pygame
import os
import random
from math import inf
from typing import Any


class Hub:
    def __init__(
            self, name: str, x: int, y: int,
            color: str, zone: str, max_drones: int):
        self.name = name
        self.x = x
        self.y = y
        self.color = color
        self.zone = zone
        self.max_drones = int(max_drones)
        self.position_on_window = (-1, -1)
        self.cost: float = self.get_cost(self)
        self.corrent_number_of_drones = 0

    def get_cost(self, hub: Any) -> float:
        if hub.zone == "blocked":
            return inf
        elif hub.zone == "priority":
            return 0.5
        elif hub.zone == "normal":
            return 1
        elif hub.zone == "restricted":
            return 2
        return inf

    @staticmethod
    def get_hub(name: str, hubs: list) -> Any:
        for hub in hubs:
            if hub.name == name:
                return hub
        return None

    def can_enter_hub(self) -> bool:
        if self.zone == "blocked":
            return False
        return self.corrent_number_of_drones < self.max_drones

    def __lt__(self, other: Any) -> bool:
        return self.get_cost(self) < self.get_cost(other)

    def __repr__(self) -> str:
        return self.name


class Graph:
    def __init__(
            self, hubs: list[Hub],
            connections: list[tuple[str, str, int]]) -> None:
        self.nodes: dict[Hub, list[Edge]] = {}
        for connection in connections:
            hub1 = Hub.get_hub(connection[0], hubs)
            hub2 = Hub.get_hub(connection[1], hubs)
            Edge.add_edge(self, hub1, hub2)
            Edge.add_edge(self, hub2, hub1)

    def __repr__(self) -> str:
        rep = ""
        for key, value in self.nodes.items():
            rep += f"{key} = {value}\n"
        return rep


class Edge:
    def __init__(self, cost: float, target: Hub) -> None:
        self.cost: float = cost
        self.target: Hub = target

    @staticmethod
    def is_there(name: str, list_hubs: list) -> bool:
        for edge in list_hubs:
            if name == edge.target.name:
                return True
        return False

    @staticmethod
    def add_edge(graph: Graph, hub1: Hub, hub2: Hub) -> None:
        if graph.nodes.get(hub1, None) is None:
            edge = Edge(hub2.cost, hub2)
            graph.nodes[hub1] = [edge]
        else:
            edge = Edge(hub2.cost, hub2)
            if not Edge.is_there(hub2.name, graph.nodes[hub1]):
                graph.nodes[hub1].append(edge)

    def __repr__(self) -> str:
        return f"cost={self.cost} target={self.target}"


class Drone:

    def __init__(self, start_hub: Hub, target_hub: Hub, Id: int):
        drones_imgs = os.listdir("fotos")
        self.img_path = f"fotos/{random.choice(drones_imgs)}"
        self.img = pygame.transform.scale(
            pygame.image.load(self.img_path), (70, 70))
        self.id = Id
        self.corrent_hub = start_hub
        self.corrent_position = start_hub.position_on_window
        self.current_target: Hub | None = None
        self.reach_target: bool = False
        self.in_transit: bool = False

    def show(self, window: pygame.Surface, img_x: int, img_y: int) -> None:
        window.blit(self.img, (img_x - 30, img_y - 30))
