import sys

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
                x=data[2],
                y=data[3],
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
        print(hub)
    for connection in connections:
        print(connection)

    # print(hubs)
    # print(connections)



# ◦ zone=<type> (default: normal)
# ◦ color=<value> (default: none)
# ◦ max_drones=<number> (default: 1) - Maximum drones that can occupy this
# zone simultaneously
# ◦ Tags inside brackets can appear in any order.


if __name__ == "__main__":
    main()