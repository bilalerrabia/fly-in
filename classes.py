import pygame
import os
import random

from dijkstra import djikstra
# from main import get_hub


def get_hub(name, hubs):
    for hub in hubs:
        if hub.name == name:
            return hub


class Graph:
    def __init__(self):
        self.nodes: dict[Hub: list[Edge]] = {}

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
        elif hub.zone == "normal" or hub.zone == "priority":
            return 1
        elif hub.zone == "restricted":
            return 2

    def __lt__(self, other):
        return self.get_cost(self) < self.get_cost(other)


class Edge:
    def __init__(self, cost, target):
        self.cost: int = cost
        self.target: Hub = target

    def __repr__(self):
        return f"cost={self.cost} target={self.target}"
class Drone:

    def __init__(self, start_hub: Hub, target_hub: Hub):

        folder_path = "fotos"
        drones_imgs = os.listdir(folder_path)
        self.img = "fotos/"
        self.img += random.choice(drones_imgs)
        self.corrent_hub = start_hub
        self.corrent_position = start_hub.position_on_window
        self.start_hub: Hub = start_hub
        self.target_hub: Hub = target_hub
        self.passed_hubs: list[Hub] = [start_hub]
        self.next_move: tuple = (-1, -1)
        self.can_move: bool = True
        self.reach_target: bool = False
        self.path: list[Hub] = []
        self.path_index: int = 0
        self.current_target: Hub = start_hub
        self.speed: float = 1.0

    def set_path(self, graph, cost_func=None):
        self.path = djikstra(graph, self.corrent_hub, self.target_hub, cost_func)
        if len(self.path) <= 1:
            self.reach_target = True
            self.current_target = self.target_hub
        else:
            self.current_target = self.path[1]

    def show(self, window, img_x, img_y):
        img = pygame.image.load(self.img)
        img = pygame.transform.scale(img, (70, 70))
        window.blit(img, (int(img_x - 30), int(img_y - 30)))