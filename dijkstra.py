# from classes import Graph, Hub, Edge
import heapq

def djikstra(graph, start_hub, target_hub, cost_func=None):
    if cost_func is None:
        cost_func = lambda h: h.cost  # Default to static zone-based cost
    previous = {v: None for v in graph.nodes.keys()}
    visited = {v: False for v in graph.nodes.keys()}
    costs = {v: float("inf") for v in graph.nodes.keys()}
    costs[start_hub] = 0
    queue = []
    heapq.heappush(queue, (0, start_hub))
    while queue:
        removed_cost, removed_hub = heapq.heappop(queue)
        visited[removed_hub] = True
        for edge in graph.nodes[removed_hub]:
            if visited[edge.target]:
                continue
            new_cost = removed_cost + cost_func(edge.target)
            if new_cost < costs[edge.target]:
                costs[edge.target] = new_cost
                previous[edge.target] = removed_hub
                heapq.heappush(queue, (new_cost, edge.target))

    path: list[Hub] = []
    current = target_hub
    while current != start_hub:
        path.append(current)
        current = previous.get(current)
        if current is None:
            return []  # No path
    path.append(start_hub)
    path.reverse()
    return path