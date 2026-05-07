import sys
from classes import Hub


def parse_metadata(line: str, counter: int) -> dict[str, str]:
    metadata: dict[str, str] = {}
    if line.find("[") > line.find("]"):
        raise ValueError(f"invalid meta_data line {counter}")
    if "[" in line and "]" in line:
        meta_data_str = line[line.find("[") + 1: line.find("]")]
        meta_data_str.strip()
        if not meta_data_str:
            raise ValueError(f"invalid meta_data line {counter}")

        meta_data_list = meta_data_str.split()
        for meta_data in meta_data_list:
            if meta_data.find("=") == -1:
                raise ValueError(f"invalid meta_data line {counter}")
            key, value = meta_data.split("=")
            if not key or not value:
                raise ValueError(f"invalid key=value on line {counter}")
            if metadata.get(key, -1) != -1:
                raise ValueError(f"override metadata on line {counter}")
            metadata[key] = value
    elif ("[" in line and "]" not in line or
        "]" in line and "[" not in line):
        raise ValueError(f"invalid metadata (line = {counter})")
    return metadata


def parse_hub(hubs: list[Hub], line: str, counter: int):
    data = line.split()
    meta_data_dict = parse_metadata(line, counter)
    for meta_data in meta_data_dict.keys():
        if meta_data == "max_drones" and  0 >= int(meta_data_dict["max_drones"]):
            raise ValueError(f"invalid number for max_drones (line = {counter})")
        if meta_data.lower() not in ["color", "max_drones", "zone"]:
            raise ValueError(
                "invalid metadata for hubs you can use only"
                f"['color', 'max_drones', 'zone'] (line = {counter})"
                )
    try:
        if meta_data_dict.get("zone", "normal") not in ["blocked", "normal", "restricted", "priority"]:
            print(f"invalid zone type (line = {counter})")
            exit()

        hub = Hub(
            name=data[1],
            x=int(data[2]),
            y=int(data[3]),
            color=meta_data_dict.get("color", "none"),
            zone=meta_data_dict.get("zone", "normal"),
            max_drones=int(meta_data_dict.get("max_drones", 1))
        )
        for other_hub in hubs:
            if (hub.x, hub.y) == (other_hub.x, other_hub.y):
                raise ValueError(f" two hubs with the same coordinates")

    except Exception as e:
        raise ValueError(
            f"invalid line (line = {counter})"
            f"{e}")

    return hub


def hub_name_exists(name: str, hubs: list[Hub]) -> bool:
    return Hub.get_hub(name, hubs) is not None


def parse_connection(hubs: list[Hub], line: str, counter: int) -> tuple[str, str, int]:
    connection_names = line.split()[1]
    if connection_names.count("-") != 1:
        raise ValueError(f"invalid connection line (line = {counter})")
    first, second = connection_names.split("-")
    if first == second:
        raise ValueError(f"(mn nytk ajmi) invalid connection between the same hub in line {counter}")
    if Hub.get_hub(first, hubs) not in hubs or Hub.get_hub(second, hubs) not in hubs:
        raise ValueError(f"invalid hub name in connection line (line = {counter})")
    meta_data_dict: dict[str, str] = parse_metadata(line, counter)
    for meta_data in meta_data_dict:
        if meta_data not in ["max_link_capacity"]:
            raise ValueError(
                "invalid metadata for connections you can use only"
                f"['max_link_capacity'] (line = {counter})"
                )
    capacity = int(meta_data_dict.get("max_link_capacity", 1))
    return first, second, capacity


def parsing() -> tuple[list[Hub], list[tuple[str, str, int]], Hub, Hub, int]:

    hubs: list[Hub] = []
    hub: Hub | None = None
    connections: list[tuple[str, str, int]] = []
    nb_drones: int = -1
    start_hub: Hub | None = None
    end_hub: Hub | None = None

    try:
        file_path = sys.argv[1]
        with open(file_path) as file_handle:
            map_file = file_handle.readlines()
    except Exception as error:
        print(f"error : {error}")
        sys.exit(0)

    counter: int = 0
    try:
        for raw_line in map_file:
            line = raw_line.strip()
            counter += 1
            if not line or line.startswith("#"):
                continue

            if line.startswith("nb_drones"):
                if nb_drones != -1:
                    print(f"too many declaration for nb_drones (line = {counter})")
                    exit()
                nb_drones = int(line.split()[1])
                continue

            if line.startswith("start_hub"):
                if start_hub:
                    print(f"too many declaration for start_hub (line = {counter})")
                    exit()
                start_hub = parse_hub(hubs, line, counter)
                if hub_name_exists(start_hub.name, hubs):
                    print(f"double declaration for {start_hub.name} hub (line = {counter})")
                    exit()
                hubs.append(start_hub)
                continue

            elif line.startswith("hub"):
                hub = parse_hub(hubs, line, counter)
                if hub_name_exists(hub.name, hubs):
                    print(f"double declaration for {hub.name} hub (line = {counter})")
                    exit()
                hubs.append(hub)
                continue

            elif line.startswith("end_hub"):
                if end_hub:
                    print(f"too many declaration for end_hub (line = {counter})")
                    exit()
                end_hub = parse_hub(hubs, line, counter)
                if hub_name_exists(end_hub.name, hubs):
                    print(f"double declaration for {end_hub.name} hub (line = {counter})")
                    exit()
                hubs.append(end_hub)
                continue

            if line.startswith("connection"):
                connection = parse_connection(hubs, line, counter)
                if (
                    connection in connections or 
                    (connection[1], connection[0], connection[2]) in connections):
                    raise ValueError(
                        "two connections between two hubs with the"
                        f" same max_link_capacity on line {counter}")
                connections.append(connection)

        if start_hub is None or end_hub is None or nb_drones == -1:
            print("error : missing start_hub or end_hub or nb_drones")
            exit()
    except Exception as e:
        raise ValueError(f"Map parsing failed: {e}")
    return hubs, connections, start_hub, end_hub, nb_drones
