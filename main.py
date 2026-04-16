import sys
import pygame
from time import sleep
import math
from classes import Hub, Graph, Edge
from dijkstra import djikstra
hubs: list[Hub] = []
connections: list[tuple[str, str]] = []

def get_hub(name, hubs):
    for hub in hubs:
        if hub.name == name:
            return hub

def is_there(name: str, list_hubs : list[Edge]):
    for edge in list_hubs:
        if name == edge.target.name:
            return True
    return False


def add_edge(graph: Graph, hub1: Hub, hub2: Hub):
    if graph.nodes.get(hub1, None) == None:
        edge = Edge(hub2.cost, hub2)
        graph.nodes[hub1] = [edge]
    else:
        edge = Edge(hub2.cost, hub2)
        if not is_there(hub2.name, graph.nodes[hub1]):
            graph.nodes[hub1].append(edge)


def main():
    global hubs
    try:
        file_path = sys.argv[1]
        with open(file_path, "r") as f:
            map_file = f.readlines()
            # for line in map_file:
            #     print(line)
    except (IOError, IndexError) as e:
        print(f"error : {e}")
        sys.exit(0)
    # print(map_file)
    nb_drones = -1
    
    for line in map_file:
        # print(line)
        if line.startswith("#"):
            continue

        elif line.startswith("nb_drones"):
            nb_drones = int(line.split()[1])

        elif (
            line.startswith("start_hub")
            or line.startswith("hub")
            or line.startswith("end_hub")):
            data = line.split()
            if line.find("[") != -1:
                meta_data_str = line[line.find("[") + 1: line.find("]")]
                # print(meta_data_str)
                meta_data_list = meta_data_str.split()
                meta_data_dict = {
                    meta_data_list[i].split("=")[0]:
                    meta_data_list[i].split("=")[1]
                    for i in range(len(meta_data_list))}
                # print(meta_data_dict)
            hub = Hub(
                name=data[1],
                x=int(data[2]),
                y=int(data[3]),
                color=meta_data_dict.get("color", "none"),
                zone=meta_data_dict.get("zone", "normal"),
                max_drones=meta_data_dict.get("max_drones", 1)
            )
            hubs.append(hub)
            # print(hubs)
            if line.startswith("start_hub"):
                    start_hub: Hub = hub
            elif line.startswith("end_hub"):
                    target_hub: Hub = hub

        elif line.startswith("connection"):
            connections.append(
                (
                    line.split()[1].split("-")[0],
                    line.split()[1].split("-")[1]
                )
            )

    colors = {
    "black" : (0, 0, 0),
    "gray" : (127, 127, 127),
    "background" : (0, 204, 204),
    "white" : (255, 255, 255),
    "crimson" : (220, 20, 60),
    "red" : (255, 0, 0),
    "darkred" : (139, 0, 0),
    "green" : (0, 255, 0),
    "blue" : (0, 0, 255),
    "gold" : (255, 255, 0),
    "maroon" : (176, 48, 96),
    "purple" : (255, 0, 255),
    "violet" : (238, 130, 238),
    "brown" : (165, 42, 42),
    "orange" : (255, 165, 0),
    "rainbow" : (127, 255, 0),
    "crimson" : (220, 20, 60),
    "yellow" : (255, 255, 0)
    }


    avg_x = sum(h.x for h in hubs) / len(hubs)
    avg_y = sum(h.y for h in hubs) / len(hubs)

    graph = Graph()
    for hub in hubs:
        for connection in connections:
            if hub.name == connection[0]:
                add_edge(graph, hub, get_hub(connection[1], hubs))
                add_edge(graph, get_hub(connection[1], hubs), hub)
                # (hub, [connection[1]]) 
                # (connection[1], [hub])
            elif hub.name == connection[1]:
                add_edge(graph, hub, get_hub(connection[0], hubs))
                add_edge(graph, get_hub(connection[0], hubs), hub)
                # (hub, [connection[0]])
                # (connection[0], [hub])
    for key, value in graph.nodes.items():
        graph.nodes[key] = list(set(value))
        # i = list(set(i))
    path: list[Hub] = djikstra(graph, start_hub, target_hub)
    drone = pygame.image.load("136.png")
    drone = pygame.transform.scale(drone, (60, 60))
    
    speed = 1
    path_index = 1
    current_target = path[path_index] if len(path) > 1 else target_hub


    width, height = 1700, 1000
    for hub in hubs:
        x = width // 2 + (hub.x - avg_x) * 60
        y = height // 2 + (hub.y - avg_y) * 160
        hub.position_on_window = (x, y)
    img_x, img_y = start_hub.position_on_window
    window = pygame.display.set_mode((width, height))
    window.fill(colors["background"])
    pygame.display.set_caption("fly-in okda ajmi chkt3raf")
    iran_frames = [pygame.image.load(f"iran/{i}.gif") for i in range(31)]
    purk_frames = [pygame.image.load(f"purk/{i}.gif") for i in range(15)]
    frame_index_iran = 0
    frame_index_purk = 0
    frame_delay_iran = 30
    frame_delay_purk = 14
    counter_iran = 0
    counter_purk = 0

    run = True
    while run:
        window.fill(colors["background"])
        for connection in connections:
            # print(hubs)
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

        for hub in hubs:
            if hub.color == "none" or hub.color not in colors:
                pygame.draw.circle(window, colors["green"], (hub.position_on_window[0], hub.position_on_window[1]), 20)
            else:
                pygame.draw.circle(window, colors[hub.color], (hub.position_on_window[0], hub.position_on_window[1]), 20)

        counter_iran += 1
        if counter_iran >= frame_delay_iran:
            frame_index_iran = (frame_index_iran + 1) % len(iran_frames)
            counter_iran = 0
        img = pygame.transform.scale(iran_frames[frame_index_iran], (100, 70))
        window.blit(
            img,
            (
                start_hub.position_on_window[0] - 50,
                start_hub.position_on_window[1] - 100
            ))
        counter_purk += 1
        if counter_purk >= frame_delay_purk:
            frame_index_purk = (frame_index_purk + 1) % len(purk_frames)
            counter_purk = 0
        img = pygame.transform.scale(purk_frames[frame_index_purk], (100, 70))
        window.blit(
            img,
            (
                target_hub.position_on_window[0] - 50,
                target_hub.position_on_window[1] - 100
            ))

        target = current_target.position_on_window
        dx = target[0] - img_x
        dy = target[1] - img_y

        dist = math.sqrt(dx*dx + dy*dy)

        if dist != 0:
            dx /= dist
            dy /= dist

        img_x += dx * speed
        img_y += dy * speed

        if dist < 5:  # reached the target
            path_index += 1
            if path_index < len(path):
                current_target = path[path_index]
            else:
                current_target = target_hub  # stay at end

        # draw moving image
        window.blit(drone, (int(img_x - 30), int(img_y - 30)))

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