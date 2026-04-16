from classes import Graph, Hub, Edge
import heapq

def djikstra(graph: Graph, start_hub: Hub, target_hub: Hub):
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
            new_cost = removed_cost + edge.cost
            if new_cost < costs[edge.target]:
                costs[edge.target] = new_cost
                previous[edge.target] = removed_hub
                heapq.heappush(queue, (new_cost, edge.target))

    path: list[Hub] = []
    while target_hub != start_hub:
        path.append(target_hub)
        target_hub = previous[target_hub]
    path.append(start_hub)
    path.reverse()
    return path