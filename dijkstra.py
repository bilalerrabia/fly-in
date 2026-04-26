# # from classes import Graph, Hub, Edge
# import heapq
# from math import inf

# def djikstra(graph, start_hub, target_hub):
#     # print("hhhhhhhhhhhhhhhhhhhhhhhhhhhh")
#     cost_func = lambda h: inf if h.zone == "blocked" else h.cost
#     all_nodes = set(graph.nodes.keys())
#     for edges in graph.nodes.values():
#         for edge in edges:
#             all_nodes.add(edge.target)

#     all_nodes.add(start_hub)
#     all_nodes.add(target_hub)

#     previous = {v: None for v in all_nodes}
#     visited = {v: False for v in all_nodes}
#     costs = {v: inf for v in all_nodes}
#     costs[start_hub] = 0
#     queue = []
#     heapq.heappush(queue, (0, start_hub))
#     while queue:
#         removed_cost, removed_hub = heapq.heappop(queue)
#         if visited[removed_hub]:
#             continue
#         visited[removed_hub] = True
#         if removed_hub == target_hub:
#             break
#         for edge in graph.nodes.get(removed_hub, []):
#             # if not graph.edge_available(removed_hub, edge.target):
#             #     continue
#             if visited[edge.target]:
#                 continue
#             target_cost = cost_func(edge.target)
#             if target_cost == inf:
#                 continue
#             new_cost = removed_cost + target_cost
#             if new_cost < costs[edge.target]:
#                 costs[edge.target] = new_cost
#                 previous[edge.target] = removed_hub
#                 heapq.heappush(queue, (new_cost, edge.target))

#     path: list[Hub] = []
#     current = target_hub
#     while current != start_hub:
#         path.append(current)
#         current = previous.get(current)
#         if current is None:
#             return []  # No path
#     path.append(start_hub)
#     path.reverse()
#     return path