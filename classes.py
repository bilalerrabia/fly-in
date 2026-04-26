import pygame
import os
import random

from dijkstra import djikstra
from some_parameters import colors
from draw_flags import draw_flags


class Graph:
    def __init__(self, hubs: list, connections: list):
        self.nodes: dict[Hub: list[Edge]] = {}
        self.link_capacity: dict[set, int] = {}
        self.link_load: dict[set, int] = {}
        for connection in connections:
            hub1 = Hub.get_hub(connection[0], hubs)
            hub2 = Hub.get_hub(connection[1], hubs)
            capacity = connection[2]
            Edge.add_edge(self, hub1, hub2, capacity)
            Edge.add_edge(self, hub2, hub1, capacity)

    def add_link(self, hub1, hub2, capacity: int = 1):
        key = (hub1.name, hub2.name)
        self.link_capacity[key] = int(capacity)
        self.link_load.setdefault(key, 0)

    def edge_load(self, hub1, hub2):
        return self.link_load.get((hub1.name, hub2.name), 0)

    def edge_available(self, hub1, hub2):
        return self.edge_load(hub1, hub2) < 1

    def reserve_edge(self, hub1, hub2):
        key = (hub1.name, hub2.name)
        self.link_load[key] = self.link_load.get(key, 0) + 1

    def release_edge(self, hub1, hub2):
        key = (hub1.name, hub2.name)
        self.link_load[key] = max(0, self.link_load.get(key, 0) - 1)

    def __repr__(self):
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

    def __repr__(self):
        return self.name

    def get_cost(self, hub):
        if hub.zone == "blocked":
            return float("inf")
        elif hub.zone == "priority":
            return 0.5
        elif hub.zone == "normal":
            return 1
        elif hub.zone == "restricted":
            return 2

    @staticmethod
    def get_hub(name, hubs):
        for hub in hubs:
            if hub.name == name:
                return hub


    @staticmethod
    def can_enter_hub(hub, start_hub, target_hub) -> bool:
        if hub in (start_hub, target_hub):
            return True
        if hub.zone == "blocked":
            return False
        return hub.corrent_number_of_drones < hub.max_drones


    def draw_hubs(window, hubs):
        for hub in hubs:
            if hub.color == "none" or hub.color not in colors:
                pygame.draw.circle(window, colors["green"], (hub.position_on_window[0], hub.position_on_window[1]), 20)
            else:
                pygame.draw.circle(window, colors[hub.color], (hub.position_on_window[0], hub.position_on_window[1]), 20)

    def __lt__(self, other):
        return self.get_cost(self) < self.get_cost(other)


class Edge:
    def __init__(self, cost, target, capacity=1):
        self.cost: int = cost
        self.target: Hub = target
        self.capacity: int = int(capacity)

    @staticmethod
    def is_there(name: str, list_hubs: list):
        for edge in list_hubs:
            if name == edge.target.name:
                return True
        return False

    @staticmethod
    def add_edge(graph: Graph, hub1: Hub, hub2: Hub, capacity: int = 1):
        graph.add_link(hub1, hub2, capacity)
        if graph.nodes.get(hub1, None) is None:
            edge = Edge(hub2.cost, hub2, capacity)
            graph.nodes[hub1] = [edge]
        else:
            edge = Edge(hub2.cost, hub2, capacity)
            if not Edge.is_there(hub2.name, graph.nodes[hub1]):
                graph.nodes[hub1].append(edge)

    def draw_connections(window, connections, hubs):
        for connection in connections:
            first_hub = Hub.get_hub(connection[0], hubs)
            second_hub = Hub.get_hub(connection[1], hubs)
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

    def __repr__(self):
        return f"cost={self.cost} target={self.target} capacity={self.capacity}"

class Drone:

    def __init__(self, start_hub: Hub, target_hub: Hub, identifier: int):

        folder_path = "fotos"
        drones_imgs = os.listdir(folder_path)
        self.img = os.path.join(folder_path, random.choice(drones_imgs))
        self.sprite = pygame.transform.scale(pygame.image.load(self.img), (70, 70))
        self.identifier = identifier
        self.corrent_hub = start_hub
        self.corrent_position = start_hub.position_on_window
        self.display_position = start_hub.position_on_window
        self.start_hub: Hub = start_hub
        self.target_hub: Hub = target_hub
        self.passed_hubs: list[Hub] = [start_hub]
        self.next_move: tuple = (-1, -1)
        self.can_move: bool = True
        self.reach_target: bool = False
        self.path: list[Hub] = []
        self.path_index: int = 0
        self.current_target: Hub | None = start_hub
        self.speed: float = 1.0
        self.in_transit: bool = False
        self.turns_remaining: int = 0
        self.transit_connection_name: str | None = None
        self.active_edge: tuple[Hub, Hub] | None = None

    def set_path(self, graph):
        self.path = djikstra(graph, self.corrent_hub, self.target_hub)
        if len(self.path) > 1:
            self.current_target = self.path[1]
        else:
            self.current_target = None

    def show(self, window, img_x, img_y):
        window.blit(self.sprite, (int(img_x - 30), int(img_y - 30)))

