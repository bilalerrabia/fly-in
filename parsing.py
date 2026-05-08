import sys
from classes import Hub

class ParsingError(Exception):
    pass

def parse_metadata(line: str, counter: int) -> dict[str, str]:
    metadata: dict[str, str] = {}
    if line.find("[") > line.find("]"):
        raise ParsingError(f"invalid meta_data line {counter}\n{line}")
    if line.find("[") == -1 and line.find("]") == -1:
        if len(line.split()) > 4:
            raise ParsingError(f"invalid meta_data line {counter}\n{line}")
    if "[" in line and "]" in line:
        if line.split()[-1].find("]") == -1:
            raise ParsingError(f"invalid meta_data line {counter}\n{line}")
        meta_data_str = line[line.find("[") + 1: line.find("]")]
        meta_data_str.strip()
        if not meta_data_str:
            raise ParsingError(f"invalid meta_data line {counter}\n{line}")

        meta_data_list = meta_data_str.split()
        for meta_data in meta_data_list:
            if meta_data.find("=") == -1:
                raise ParsingError(f"invalid meta_data line {counter}\n{line}")
            key, value = meta_data.split("=")
            key = key.strip()
            value = value.strip()
            if not key or not value:
                raise ParsingError(f"invalid key=value on line {counter}\n{line}")
            if metadata.get(key, -1) != -1:
                raise ParsingError(f"override metadata on line {counter}\n{line}")
            metadata[key] = value
    elif ("[" in line and "]" not in line or
        "]" in line and "[" not in line):
        raise ParsingError(f"invalid metadata (line = {counter})\n{line}")
    return metadata


def parse_hub(hubs: list[Hub], line: str, counter: int):
    data = line.split()
    meta_data_dict = parse_metadata(line, counter)
    for meta_data in meta_data_dict.keys():
        if meta_data == "max_drones" and  0 >= int(meta_data_dict["max_drones"]):
            raise ParsingError(f"invalid number for max_drones (line = {counter})\n{line}")
        if meta_data.lower() not in ["color", "max_drones", "zone"]:
            raise ParsingError(
                "invalid metadata for hubs you can use only"
                f"['color', 'max_drones', 'zone'] (line = {counter})"
                f"\n{line}"
                )

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
            raise ParsingError(f" two hubs with the same coordinates \n{line}")
    return hub


def hub_name_exists(name: str, hubs: list[Hub]) -> bool:
    return Hub.get_hub(name, hubs) is not None


def parse_connection(hubs: list[Hub], line: str, counter: int) -> tuple[str, str, int]:
    connection_names = line.split()[1]
    if connection_names.count("-") != 1:
        raise ParsingError(f"invalid connection line (line = {counter})\n{line}")
    first, second = connection_names.split("-")
    if first == second:
        raise ParsingError(f"(mn nytk ajmi) invalid connection between the same hub in line {counter}\n{line}")
    if Hub.get_hub(first, hubs) not in hubs or Hub.get_hub(second, hubs) not in hubs:
        raise ParsingError(f"invalid hub name in connection line (line = {counter})\n{line}")
    meta_data_dict: dict[str, str] = parse_metadata(line, counter)
    for meta_data in meta_data_dict:
        if meta_data not in ["max_link_capacity"]:
            raise ParsingError(
                "invalid metadata for connections you can use only"
                f"['max_link_capacity'] (line = {counter})"
                f"\n{line}"
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
        with open(file_path) as file_handel:
            map_file = file_handel.readlines()
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

            elif line.count(":") != 1:
                    raise ParsingError(f"invalid line (line = {counter}) \n {line}")

            elif line.find("==") != -1:
                raise ParsingError(f"invalid syntax in line = {counter} \n{line}")
            elif line.startswith("nb_drones"):
                if line.count(":") != 1:
                    raise ParsingError(f"invalid line for nb_drones (line = {counter}) \n {line}")
                if hubs or connections:
                    raise ParsingError(f"nb_drones have to be define first (line = {counter})\n{line}")
                if nb_drones != -1:
                    print(f"too many declaration for nb_drones (line = {counter})")
                    exit()
                nb_drones = int(line.split(":")[1])
                if nb_drones < 0:
                    raise ParsingError(f"nb_drones can't be negative line = {counter} \n{line}")
                continue

            elif line.startswith("start_hub"):
                if start_hub:
                    print(f"too many declaration for start_hub (line = {counter})")
                    exit()
                start_hub = parse_hub(hubs, line, counter)
                if start_hub.max_drones < nb_drones:
                    raise ParsingError(f"start_hub max_drones not enough for the nb_drones (line = {counter})\n{line}")
                # if hub_name_exists(start_hub.name, hubs):
                #     print(f"double declaration for {start_hub.name} hub (line = {counter})")
                #     exit()
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

            elif line.startswith("connection"):
                connection = parse_connection(hubs, line, counter)
                if (
                    connection in connections or 
                    (connection[1], connection[0], connection[2]) in connections):
                    raise ParsingError(
                        "two connections between two hubs with the"
                        f" same max_link_capacity on line {counter}\n{line}")
                connections.append(connection)
            else:
                raise ParsingError(f"invalid line at (line= {counter})\n{line}")

        if start_hub is None or end_hub is None or nb_drones == -1:
            print("error : missing start_hub or end_hub or nb_drones")
            exit()
    except Exception as e:
        raise ParsingError(f"error: {e}")
    return hubs, connections, start_hub, end_hub, nb_drones
