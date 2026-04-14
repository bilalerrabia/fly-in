import sys
import pygame

class Hub:
    def __init__(self, name: str, x: int, y: int, color: str, zone: str, max_drones: int):
        self.name = name
        self.x = x
        self.y = y
        self.color = color
        self.zone = zone
        self.max_drones = max_drones
    def __repr__(self):
        return f"name={self.name} color={self.color} zone={self.zone} x={self.x} y={self.y} max_drones={self.max_drones}"

hubs: list[Hub] = []
connections: list[tuple[str, str]] = []
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
    for hub in hubs:
        print(hub.color)
    for connection in connections:
        print(connection)

    # print(hubs)
    # print(connections)
    colors = {
    "black" : (0, 0, 0),
    "gray" : (127, 127, 127),
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
    # background = pygame.image.load("ana.jpg")
    width, height = 1500, 1000
    # width, height = background.get_size()
    window = pygame.display.set_mode((width, height))
    # background = pygame.transform.scale(background, (1000, 1000))
    window.fill(colors["gray"])
    pygame.display.set_caption("fly-in okda ajmi chkt3raf")
    run = True
    while run:
        # 1. Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        # window.blit(background, (0, 0))
        # 3. Draw everything
        for hub in hubs:
            print(hub)
            avg_x = sum(h.x for h in hubs) / len(hubs)
            avg_y = sum(h.y for h in hubs) / len(hubs)

            window.fill(colors["gray"])

            for hub in hubs:
                x = width // 2 + (hub.x - avg_x) * 100
                y = height // 2 + (hub.y - avg_y) * 100

                if hub.color == "none" or hub.color not in colors:
                    pygame.draw.circle(window, colors["green"], (int(x), int(y)), 30)
                else:
                    pygame.draw.circle(window, colors[hub.color], (int(x), int(y)), 30)

            pygame.display.update()
    # print(len(hubs), "ff")
    for hub in hubs:
        print(hub.color)
    print(len(hubs))
if __name__ == "__main__":
    main()