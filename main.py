import math
import sys
from time import sleep
import pygame

from classes import Drone, Edge, Graph, Hub
from draw_flags import draw_flags
from hub_scoring_router import ScoreBasedRouter
from some_parameters import colors
from parsing import parsing


def draw_hubs(window: pygame.Surface, hubs: list[Hub]) -> None:
    for hub in hubs:
        if hub.color == "none" or hub.color not in colors:
            pygame.draw.circle(
                window,
                colors["green"],
                (hub.position_on_window[0], hub.position_on_window[1]),
                20,
            )
        else:
            pygame.draw.circle(
                window,
                colors[hub.color],
                (hub.position_on_window[0], hub.position_on_window[1]),
                20,
            )


def draw_connections(
    window: pygame.Surface,
    connections: list[tuple[str, str, int]],
    hubs: list[Hub],
) -> None:
    for connection in connections:
        if Hub.get_hub(connection[0], hubs).zone == "blocked":
            color = colors["red"]
        elif Hub.get_hub(connection[0], hubs).zone == "priority":
            color = colors["green"]
        elif Hub.get_hub(connection[0], hubs).zone == "restricted":
            color = colors["darkred"]
        else:
            color = colors["white"]

        pygame.draw.line(
            window,
            color,
            Hub.get_hub(connection[0], hubs).position_on_window,
            Hub.get_hub(connection[1], hubs).position_on_window,
            width=3,
        )


def init_the_graph(
    graph: Graph,
    hubs: list[Hub],
    connections: list[tuple[str, str, int]],
) -> None:
    for connection in connections:
        hub1 = Hub.get_hub(connection[0], hubs)
        hub2 = Hub.get_hub(connection[1], hubs)
        capacity = connection[2]
        Edge.add_edge(graph, hub1, hub2, capacity)
        Edge.add_edge(graph, hub2, hub1, capacity)


def hub_midpoint(hub1: Hub, hub2: Hub) -> tuple[float, float]:
    return (
        (hub1.position_on_window[0] + hub2.position_on_window[0]) / 2,
        (hub1.position_on_window[1] + hub2.position_on_window[1]) / 2,
    )


def lerp_position(
    start: tuple[float, float],
    end: tuple[float, float],
    progress: float,
) -> tuple[float, float]:
    return (
        start[0] + (end[0] - start[0]) * progress,
        start[1] + (end[1] - start[1]) * progress,
    )


def main() -> None:
    pygame.init()

    font = pygame.font.SysFont(None, 32)

    def write_text(window: pygame.Surface, txt: str) -> None:
        text_surface = font.render(txt, True, (255, 255, 255))
        window.blit(text_surface, (50, 100))

    hubs: list[Hub] = []
    connections: list[tuple[str, str, int]] = []
    start_hub: Hub | None = None
    target_hub: Hub | None = None

    hubs, connections, start_hub, target_hub, nb_drones = parsing(hubs, connections, start_hub, target_hub)


    avg_x = sum(hub.x for hub in hubs) / len(hubs)
    avg_y = sum(hub.y for hub in hubs) / len(hubs)

    graph = Graph()
    init_the_graph(graph, hubs, connections)

    start_hub.max_drones = max(start_hub.max_drones, nb_drones)
    target_hub.max_drones = max(target_hub.max_drones, nb_drones)

    def cost_func(hub: Hub) -> float:
        if hub.zone == "blocked":
            return float("inf")
        return hub.cost

    score_margin = 0.0

    width, height = 1700, 1000
    for hub in hubs:
        x = width // 2 + (hub.x - avg_x) * 60
        y = height // 2 + (hub.y - avg_y) * 160
        hub.position_on_window = (x, y)

    window = pygame.display.set_mode((width, height))
    pygame.display.set_caption("fly-in okda ajmi chkt3raf")

    drones: list[Drone] = [
        Drone(drone_id, start_hub, target_hub)
        for drone_id in range(1, nb_drones + 1)
    ]
    start_hub.corrent_number_of_drones = nb_drones

    router = ScoreBasedRouter(graph, target_hub, cost_func, score_margin=score_margin)
    turn_number = 0

    def draw_scene(turn_label: str) -> None:
        window.fill(colors["background"])
        draw_connections(window, connections, hubs)
        draw_hubs(window, hubs)
        draw_flags(window, start_hub, target_hub)
        write_text(window, turn_label)
        for drone in drones:
            drone.show(window, drone.corrent_position[0], drone.corrent_position[1])
        pygame.display.update()

    def animate_turn_movements(
        movement_segments: list[tuple[Drone, tuple[float, float], tuple[float, float], str]],
        turn_label: str,
        frames: int = 12,
    ) -> None:
        if not movement_segments:
            draw_scene(turn_label)
            sleep(0.05)
            return

        for frame in range(frames):
            progress = (frame + 1) / frames
            for drone, start_position, end_position, _ in movement_segments:
                drone.corrent_position = lerp_position(start_position, end_position, progress)
            draw_scene(turn_label)
            sleep(0.02)

        for drone, _, end_position, move_kind in movement_segments:
            drone.corrent_position = end_position
            if move_kind == "normal_launch" and drone.active_edge is not None:
                graph.release_edge(*drone.active_edge)
                drone.active_edge = None
            elif move_kind == "restricted_arrival" and drone.active_edge is not None:
                graph.release_edge(*drone.active_edge)
                drone.active_edge = None
                drone.finish_restricted_move()

        draw_scene(turn_label)
        sleep(0.02)

    run = True
    while run:
        turn_number += 1
        turn_events: list[str] = []
        movement_segments: list[tuple[Drone, tuple[float, float], tuple[float, float], str]] = []

        for drone in drones:
            if not drone.in_transit or drone.transit_destination is None:
                continue

            if drone.transit_remaining_turns > 0:
                drone.transit_remaining_turns -= 1

            if drone.transit_remaining_turns == 0:
                turn_events.append(f"D{drone.drone_id}-{drone.transit_destination.name}")
                movement_segments.append(
                    (
                        drone,
                        drone.corrent_position,
                        drone.transit_destination.position_on_window,
                        "restricted_arrival",
                    )
                )
        router.refresh_scores()

        movable_drones = [drone for drone in drones if Drone.is_drone_movable(drone)]
        movable_drones.sort(
            key=lambda drone: (
                router.hub_scores.get(drone.corrent_hub).forward_options
                if router.hub_scores.get(drone.corrent_hub) is not None else 0,
                router.distance_to_target.get(drone.corrent_hub, math.inf),
                drone.drone_id,
            )
        )

        for drone in movable_drones:
            next_hub = router.choose_next_hub(drone)
            if next_hub is None:
                continue

            origin = drone.corrent_hub
            graph.reserve_edge(origin, next_hub)
            if origin != start_hub:
                origin.corrent_number_of_drones -= 1
            if next_hub != target_hub:
                next_hub.corrent_number_of_drones += 1

            drone.active_edge = (origin, next_hub)
            drone.current_target = next_hub

            if next_hub.zone == "restricted":
                drone.begin_restricted_move(
                    next_hub,
                    # f"{origin.name}-{next_hub.name}",
                    origin.position_on_window,
                )
                turn_events.append(f"D{drone.drone_id}-{origin.name}-{next_hub.name}")
                movement_segments.append(
                    (
                        drone,
                        origin.position_on_window,
                        hub_midpoint(origin, next_hub),
                        "restricted_launch",
                    )
                )
            else:
                drone.begin_normal_move(next_hub, origin.position_on_window)
                if next_hub == target_hub:
                    drone.reach_target = True
                turn_events.append(f"D{drone.drone_id}-{next_hub.name}")
                movement_segments.append(
                    (
                        drone,
                        origin.position_on_window,
                        next_hub.position_on_window,
                        "normal_launch",
                    )
                )

            router.refresh_scores()

        print(" ".join(turn_events))
        animate_turn_movements(movement_segments, f"turn = {turn_number}")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        # if all(drone.reach_target for drone in drones):
        #     run = False

    print(f"completed in {turn_number} turns")


if __name__ == "__main__":
    main()
