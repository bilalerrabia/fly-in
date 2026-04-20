from __future__ import annotations

import pygame
import os
import random

from dijkstra import djikstra


# def get_hub(name: str, hubs: list):
#     for hub in hubs:
#         if hub.name == name:
#             return hub
#     raise ValueError(f"hub not found: {name}")


class Graph:
    def __init__(self):
        self.nodes: dict[Hub: list[Edge]] = {}
        self.link_capacity: dict[frozenset[str], int] = {}
        self.link_load: dict[frozenset[str], int] = {}

    def edge_key(self, hub1: Hub, hub2: Hub) -> frozenset[str]:
        return frozenset((hub1.name, hub2.name))

    def add_link(self, hub1: Hub, hub2: Hub, capacity: int = 1) -> None:
        key = self.edge_key(hub1, hub2)
        self.link_capacity[key] = int(capacity)
        self.link_load.setdefault(key, 0)

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

    def __repr__(self) -> str:
        rep = ""
        for key, value in self.nodes.items():
            rep += f"{key} = {value}\n"
        return rep


class Hub:

    def __init__(self, name: str, x: int, y: int, color: str, zone: str, max_drones: int):
        self.name = name
        self.x = x
        self.y = y
        self.color = color
        self.zone = zone
        self.max_drones = int(max_drones)
        self.position_on_window = (-1, -1)
        self.cost = self.get_cost(self)
        self.corrent_number_of_drones = 0

    def __repr__(self) -> str:
        return self.name


    def get_cost(self, hub: Hub) -> float:
        if hub.zone == "blocked":
            return float("inf")
        elif hub.zone == "priority":
            return 1
        elif hub.zone == "normal":
            return 1
        elif hub.zone == "restricted":
            return 2
        return 1

    def __lt__(self, other: Hub) -> bool:
        return self.get_cost(self) < self.get_cost(other)

    def get_hub(name: str, hubs: list[Hub]) -> Hub:
        for hub in hubs:
            if hub.name == name:
                return hub
        raise ValueError(f"hub not found: {name}")


class Edge:
    def __init__(self, cost: float, target: Hub, capacity: int = 1):
        self.cost: float = cost
        self.target: Hub = target
        self.capacity: int = int(capacity)


    def is_there(name: str, list_hubs: list[Edge]) -> bool:
        for edge in list_hubs:
            if name == edge.target.name:
                return True
        return False


    def add_edge(graph: Graph, hub1: Hub, hub2: Hub, capacity: int = 1) -> None:
        graph.add_link(hub1, hub2, capacity)
        if graph.nodes.get(hub1, None) is None:
            edge = Edge(hub2.cost, hub2, capacity)
            graph.nodes[hub1] = [edge]
        else:
            edge = Edge(hub2.cost, hub2, capacity)
            if not Edge.is_there(hub2.name, graph.nodes[hub1]):
                graph.nodes[hub1].append(edge)


    def __repr__(self) -> str:
        return f"cost={self.cost} target={self.target} capacity={self.capacity}"


class Drone:
    def __init__(self, drone_id: int, start_hub: Hub, target_hub: Hub):

        folder_path = "fotos"
        drones_imgs = os.listdir(folder_path)
        self.img = "fotos/"
        self.img += random.choice(drones_imgs)
        self.drone_id = drone_id
        self.corrent_hub = start_hub
        self.corrent_position = start_hub.position_on_window
        self.start_hub: Hub = start_hub
        self.target_hub: Hub = target_hub
        self.next_move: tuple = (-1, -1)
        self.can_move: bool = True
        self.reach_target: bool = False
        self.path: list[Hub] = []
        self.path_index: int = 0
        self.current_target: Hub = start_hub
        # self.speed: float = 1.0
        self.in_transit: bool = False
        self.active_edge: tuple[Hub, Hub] | None = None
        self.transit_remaining_turns: int = 0
        self.transit_origin: Hub | None = None
        self.transit_destination: Hub | None = None
        # self.transit_connection_name: str = ""

    # def set_path(self, graph, cost_func=None):
    #     self.path = djikstra(graph, self.corrent_hub, self.target_hub, cost_func)
    #     if len(self.path) > 1:
    #         self.current_target = self.path[1]
    #     else:
    #         self.current_target = None

    def begin_normal_move(self, destination: Hub, start_position: tuple[float, float]) -> None:
        self.corrent_hub = destination
        self.corrent_position = start_position
        self.current_target = destination
        self.in_transit = False
        self.transit_remaining_turns = 0
        self.transit_origin = None
        self.transit_destination = None
        # self.transit_connection_name = ""

    def begin_restricted_move(
        self,
        destination: Hub,
        # connection_name: str,
        start_position: tuple[float, float],
    ) -> None:
        self.current_target = destination
        self.transit_origin = self.corrent_hub
        self.transit_destination = destination
        # self.transit_connection_name = connection_name
        self.transit_remaining_turns = 1
        self.in_transit = True
        self.corrent_position = start_position

    def finish_restricted_move(self) -> None:
        if self.transit_destination is None:
            return

        self.corrent_hub = self.transit_destination
        self.corrent_position = self.transit_destination.position_on_window
        self.in_transit = False
        self.transit_remaining_turns = 0
        self.transit_origin = None
        self.transit_destination = None
        # self.transit_connection_name = ""
        if self.corrent_hub == self.target_hub:
            self.reach_target = True

    def show(self, window, img_x, img_y):
        img = pygame.image.load(self.img)
        img = pygame.transform.scale(img, (70, 70))
        window.blit(img, (int(img_x - 30), int(img_y - 30)))


    def is_drone_movable(drone: Drone) -> bool:
        return not drone.reach_target and not drone.in_transit
