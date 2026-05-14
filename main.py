import pygame
from heapq import heappop, heappush
from math import inf
from classes import Hub, Graph, Drone
from render import Rendring
from parsing import Parsing
from typing import Any


class Solver:
    """Turn-based routing helpers for the drone scheduler."""

    @staticmethod
    def build_static_distance_map(
            graph: Graph,
            target_hub: Hub) -> dict[Hub, float]:
        """Compute the cheapest known distance from each hub to the target."""
        distances: dict[Hub, float] = {target_hub: 0.0}

        queue: list[tuple[float, Hub]] = []
        heappush(queue, (0.0, target_hub))

        while queue:
            distance, hub = heappop(queue)

            for edge in graph.nodes.get(hub, []):
                neighbor = edge.target
                if neighbor.zone == "blocked":
                    continue

                new_distance = distance + neighbor.cost
                if new_distance < distances.get(neighbor, inf):
                    distances[neighbor] = new_distance
                    heappush(queue, (new_distance, neighbor))

        return distances

    @staticmethod
    def rank_next_hubs(
        graph: Graph,
        current_hub: Any,
        static_distances: dict[Hub, float],
    ) -> list[Hub]:
        """Return neighbor hubs ordered by reverse distance from the target."""
        current_distance: float = static_distances.get(current_hub, inf)

        ranked_candidates: list[tuple[float, Hub]] = []
        for edge in graph.nodes.get(current_hub, []):
            next_hub = edge.target
            next_distance: float = static_distances.get(next_hub, inf)
            if next_distance > current_distance:
                continue
            if not next_hub.can_enter_hub():
                continue

            ranked_candidates.append((next_distance, next_hub))

        ranked_candidates.sort()
        res = [hub for _, hub in ranked_candidates]
        return res


class WriteText:

    @staticmethod
    def write_text(window: pygame.surface.Surface, txt: str) -> None:
        pygame.init()
        font = pygame.font.SysFont("", 32)
        """Render a single status line on the top left window."""
        text_surface = font.render(txt, True, (255, 255, 255))
        window.blit(text_surface, (50, 100))


def main() -> None:
    """Run the pygame simulation for the map given on sys.argv[1]."""

    try:
        (
            hubs, connections, start_hub,
            target_hub, nb_drones
        ) = Parsing().parsing()
    except Exception as e:
        print(e)
        exit()

    graph = Graph(hubs, connections)
    static_distances = Solver.build_static_distance_map(graph, target_hub)

    # init the hub.position_on_window
    avg_x = sum(hub.x for hub in hubs) / len(hubs)
    avg_y = sum(hub.y for hub in hubs) / len(hubs)
    width, height = 1700, 1000
    for hub in hubs:
        x = width // 2 + (hub.x - avg_x) * 60
        y = height // 2 + (hub.y - avg_y) * 160
        hub.position_on_window = (x, y)

    # init the pygame window
    window: pygame.surface.Surface = pygame.display.set_mode((width, height))
    pygame.display.set_caption("fly-in okda ajmi chkt3rf")

    drones: list[Drone] = [
        Drone(start_hub, index + 1)
        for index in range(nb_drones)
        ]

    clock = pygame.time.Clock()

    turn = 0
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        turn_events: list[str] = []
        turn_movements: list[
            tuple[
                Drone, tuple[
                    float, float], tuple[
                        float, float]]] = []
        arrived_this_turn: set[int] = set()

        for drone in drones:
            if not drone.in_transit or drone.reach_final_target:
                continue

            drone.in_transit = False
            arrived_this_turn.add(drone.id)

        for drone in drones:
            if (
                drone.reach_final_target or
                drone.in_transit or
                drone.id in arrived_this_turn
            ):
                continue

            ranked_candidates = Solver.rank_next_hubs(
                graph, drone.corrent_hub, static_distances)

            next_hub = ranked_candidates[0] if ranked_candidates else None

            if next_hub is None:
                continue

            if next_hub == target_hub:
                drone.reach_final_target = True

            drone.corrent_hub.corrent_number_of_drones -= 1
            next_hub.corrent_number_of_drones += 1
            drone.current_target = next_hub

            turn_movements.append(
                (
                    drone, drone.corrent_hub.position_on_window,
                    next_hub.position_on_window
                )
            )
            turn_events.append(f"D{drone.id}-{next_hub.name}")

            if next_hub.zone == "restricted":
                drone.in_transit = True

            drone.corrent_hub = next_hub

        if turn_events:
            turn += 1
            print(turn, " ".join(turn_events))

        Rendring.draw_turn(
            window, clock, connections, hubs, start_hub,
            target_hub, drones, WriteText.write_text,
            f"turn = {turn}", turn_movements)

    pygame.quit()


if __name__ == "__main__":
    main()
