import sys
import pygame
from time import sleep
import math

from some_parameters import colors
from classes import Hub, Graph, Edge, Drone
from dijkstra import djikstra
from draw_flags import draw_flags

def get_hub(name, hubs):
    for hub in hubs:
        if hub.name == name:
            return hub


def is_there(name: str, list_hubs: list[Edge]):
    for edge in list_hubs:
        if name == edge.target.name:
            return True
    return False


def add_edge(graph: Graph, hub1: Hub, hub2: Hub):
    if graph.nodes.get(hub1, None) is None:
        edge = Edge(hub2.cost, hub2)
        graph.nodes[hub1] = [edge]
    else:
        edge = Edge(hub2.cost, hub2)
        if not is_there(hub2.name, graph.nodes[hub1]):
            graph.nodes[hub1].append(edge)

def draw_hubs(window, hubs):
    for hub in hubs:
        if hub.color == "none" or hub.color not in colors:
            pygame.draw.circle(window, colors["green"], (hub.position_on_window[0], hub.position_on_window[1]), 20)
        else:
            pygame.draw.circle(window, colors[hub.color], (hub.position_on_window[0], hub.position_on_window[1]), 20)

def draw_connections(window, connections, hubs):
    for connection in connections:
        if get_hub(connection[0], hubs).zone == "blocked":
            color = colors["red"]
        elif get_hub(connection[0], hubs).zone == "priority":
            color = colors["green"]
        elif get_hub(connection[0], hubs).zone == "restricted":
            color = colors["darkred"]
        else:
            color = colors["white"]
        
        pygame.draw.line(
            window, color,
            get_hub(connection[0], hubs).position_on_window,
            get_hub(connection[1], hubs).position_on_window,
            width=3
        )

def build_the_graph(graph: Graph, hubs: list, connections: list):
    for hub in hubs:
        for connection in connections:
            if hub.name == connection[0]:
                add_edge(graph, hub, get_hub(connection[1], hubs))
                add_edge(graph, get_hub(connection[1], hubs), hub)

            elif hub.name == connection[1]:
                add_edge(graph, hub, get_hub(connection[0], hubs))
                add_edge(graph, get_hub(connection[0], hubs), hub)

def main():

    # parsing dyal l3bar
    hubs: list[Hub] = []
    connections: list[tuple[str, str]] = []
    try:
        file_path = sys.argv[1]
        with open(file_path, "r") as f:
            map_file = f.readlines()
    except (IOError, IndexError) as e:
        print(f"error : {e}")
        sys.exit(0)

    for line in map_file:
        if line.startswith("#"):
            continue

        elif line.startswith("nb_drones"):
            nb_drones = int(line.split()[1])

        elif (
            line.startswith("start_hub")
            or line.startswith("hub")
            or line.startswith("end_hub")
            ):
            data = line.split()
            if line.find("[") != -1:
                meta_data_str = line[line.find("[") + 1: line.find("]")]
                meta_data_list = meta_data_str.split()
                meta_data_dict = {
                    meta_data_list[i].split("=")[0]:
                    meta_data_list[i].split("=")[1]
                    for i in range(len(meta_data_list))}

            hub = Hub(
                name=data[1],
                x=int(data[2]),
                y=int(data[3]),
                color=meta_data_dict.get("color", "none"),
                zone=meta_data_dict.get("zone", "normal"),
                max_drones=meta_data_dict.get("max_drones", 1)
            )
            hubs.append(hub)
            if line.startswith("start_hub"):
                    start_hub = hub
            elif line.startswith("end_hub"):
                    target_hub = hub

        elif line.startswith("connection"):
            connections.append(
                (
                    line.split()[1].split("-")[0],
                    line.split()[1].split("-")[1]
                )
            )
    # baraka mn parsing


    avg_x = sum(h.x for h in hubs) / len(hubs)
    avg_y = sum(h.y for h in hubs) / len(hubs)

    graph = Graph()
    build_the_graph(graph, hubs, connections)

    penalty = 10
    cost_func = lambda h: h.cost + (h.corrent_number_of_drones / max(1, h.max_drones)) * penalty

    path: list[Hub] = djikstra(graph, start_hub, target_hub)
    drone = Drone(start_hub, target_hub)
    # drone = pygame.image.load("")
    # drone = pygame.transform.scale(drone, (60, 60))

    speed = 1 #pixel per frame
    path_index = 1
    current_target = path[path_index]

    width, height = 1700, 1000
    for hub in hubs:
        x = width // 2 + (hub.x - avg_x) * 60
        y = height // 2 + (hub.y - avg_y) * 160
        hub.position_on_window = (x, y)
    img_x, img_y = start_hub.position_on_window
    window = pygame.display.set_mode((width, height))
    window.fill(colors["background"])
    pygame.display.set_caption("fly-in okda ajmi chkt3raf")

    drones: list[Drone] = []
    for drone in range(nb_drones):
        drones.append(Drone(start_hub, target_hub))
    start_hub.corrent_number_of_drones = nb_drones
    for drone in drones:
        drone.set_path(graph, cost_func)


    run = True
    while run:

        window.fill(colors["background"])

        draw_connections(window, connections, hubs)

        draw_hubs(window, hubs)

        draw_flags(window, start_hub, target_hub)

        # if not drones[0].reach_target:

        for drone in drones:
            if drone.reach_target:
                continue
            target = drone.current_target.position_on_window
            dx = target[0] - drone.corrent_position[0]
            dy = target[1] - drone.corrent_position[1]
            dist = math.sqrt(dx**2 + dy**2)
            if dist > 0:
                dx /= dist
                dy /= dist
                drone.corrent_position = (drone.corrent_position[0] + dx * drone.speed, drone.corrent_position[1] + dy * drone.speed)
            if dist < 5:
                # reached current_target
                if drone.current_target == drone.target_hub:
                    if drone.current_target.corrent_number_of_drones < drone.current_target.max_drones:
                        drone.reach_target = True
                        drone.target_hub.corrent_number_of_drones += 1
                        drone.corrent_position = drone.current_target.position_on_window
                    else:
                        # can't enter target, stay
                        drone.corrent_position = drone.corrent_hub.position_on_window
                        drone.current_target = drone.corrent_hub
                        drone.set_path(graph, cost_func)
                else:
                    # arrived at intermediate hub
                    if drone.current_target.corrent_number_of_drones < drone.current_target.max_drones:
                        drone.corrent_hub.corrent_number_of_drones -= 1
                        drone.corrent_hub = drone.current_target
                        drone.current_target.corrent_number_of_drones += 1
                        drone.corrent_position = drone.current_target.position_on_window
                        drone.set_path(graph, cost_func)
                    else:
                        # can't enter, stay at current_hub
                        drone.corrent_position = drone.corrent_hub.position_on_window
                        drone.current_target = drone.corrent_hub
                        drone.set_path(graph, cost_func)

        for drone in drones:
            drone.show(window, drone.corrent_position[0], drone.corrent_position[1])

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        pygame.display.update()
        sleep(0.003)

    print(graph)

    print(path)

    print(len(hubs))

if __name__ == "__main__":
    main()