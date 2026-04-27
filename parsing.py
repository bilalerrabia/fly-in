import sys
from classes import Drone, Edge, Graph, Hub

def parse_metadata(line: str) -> dict[str, str]:
    metadata: dict[str, str] = {}
    if "[" in line and "]" in line:
        meta_data_str = line[line.find("[") + 1: line.find("]")]
        meta_data_list = meta_data_str.split()
        metadata = {
            meta_data_list[index].split("=")[0]: meta_data_list[index].split("=")[1]
            for index in range(len(meta_data_list))
            if "=" in meta_data_list[index]
        }
    return metadata


def parse_connection(line: str) -> tuple[str, str, int]:
    connection_name = line.split()[1]
    first, second = connection_name.split("-")
    metadata = parse_metadata(line)
    capacity = int(metadata.get("max_link_capacity", 1))
    return first, second, capacity


def parsing():

    hubs: list[Hub] = []
    connections: list[tuple[str, str, int]] = []
    nb_drones = -1
    start_hub: Hub | None = None
    target_hub: Hub | None = None

    try:
        file_path = sys.argv[1]
        with open(file_path) as file_handle:
            map_file = file_handle.readlines()
    except (IOError, IndexError) as error:
        print(f"error : {error}")
        sys.exit(0)

    for raw_line in map_file:
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        if line.startswith("nb_drones"):
            nb_drones = int(line.split()[1])
            continue

        if (
            line.startswith("start_hub")
            or line.startswith("hub")
            or line.startswith("end_hub")
        ):
            data = line.split()
            meta_data_dict = parse_metadata(line)

            hub = Hub(
                name=data[1],
                x=int(data[2]),
                y=int(data[3]),
                color=meta_data_dict.get("color", "none"),
                zone=meta_data_dict.get("zone", "normal"),
                max_drones=int(meta_data_dict.get("max_drones", 1))
            )
            hubs.append(hub)
            if line.startswith("start_hub"):
                start_hub = hub
            elif line.startswith("end_hub"):
                target_hub = hub
            continue

        if line.startswith("connection"):
            connections.append(parse_connection(line))

    if start_hub is None or target_hub is None or nb_drones == -1:
        print("error : missing start_hub or end_hub or nb_drones")
        sys.exit(0)
    return hubs, connections, start_hub, target_hub, nb_drones