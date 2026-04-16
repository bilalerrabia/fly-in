

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
        self.max_drones = max_drones
        self.position_on_window = (-1, -1)
        self.cost = self.get_cost(self)
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
