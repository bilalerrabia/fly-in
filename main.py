import sys
import pygame
import math
from classes import Hub, Graph, Edge

hubs: list[Hub] = []
connections: list[tuple[str, str]] = []

def get_cost(hub: Hub):
    if hub.zone == "blocked":
        return math.inf
    elif hub.zone == "normal" or hub.zone == "priority":
        return 1
    elif hub.zone == "restricted":
        return 2

def get_hub(name, hubs):
    for hub in hubs:
        if hub.name == name:
            return hub

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
    background = pygame.image.load("ana.jpg")
    width, height = 1700, 1000
    # width, height = background.get_size()
    window = pygame.display.set_mode((width, height))

    # background = pygame.transform.scale(background, (width, height))
    # window.blit(background, (0, 0))

    window.fill(colors["background"])
    pygame.display.set_caption("fly-in okda ajmi chkt3raf")

    avg_x = sum(h.x for h in hubs) / len(hubs)
    avg_y = sum(h.y for h in hubs) / len(hubs)

    for hub in hubs:
        x = width // 2 + (hub.x - avg_x) * 60
        y = height // 2 + (hub.y - avg_y) * 160
        hub.position_on_window = (x, y)

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
        # print(hub.position_on_window(0), hub.position_on_window(1))
        # print(hub.position_on_window)
        # pygame.display.update()

    pygame.display.update()

    run = True
    while run:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DELETE:
                    run = False

    graph = Graph()

    # for connection in connections:
    #     hub: Hub = get_hub(connection[0], hubs)

    #     if graph.nodes.get(hub, None) == None:
    #         node = get_hub(connection[1], hubs)
    #         edge = Edge(get_cost(node), node)
    #         graph.nodes[hub] = [edge]
    #     else:
    #         node = get_hub(connection[1], hubs)
    #         edge = Edge(get_cost(node), node)
    #         graph.nodes[hub].append(edge)

    def is_there(name: str, list_hubs : list[Edge]):
        for edge in list_hubs:
            if name == edge.target.name:
                return True
        return False


    def add_edge(graph: Graph, hub1: Hub, hub2: Hub):
        if graph.nodes.get(hub1, None) == None:
            edge = Edge(get_cost(hub2), hub2)
            graph.nodes[hub1] = [edge]
        else:
            edge = Edge(get_cost(hub2), hub2)
            if not is_there(hub2.name, graph.nodes[hub1]):
                graph.nodes[hub1].append(edge)

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

    print(graph)

    print(len(hubs))
if __name__ == "__main__":
    main()