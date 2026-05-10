import pygame
from typing import Callable

from draw_flags import draw_flags
from classes import Hub, Drone
from some_parameters import colors


class Rendring:

    @staticmethod
    def draw_connections(
            window: pygame.surface.Surface,
            connections: list[tuple[str, str, int]],
            hubs: list[Hub]) -> None:
        for connection in connections:
            first_hub = Hub.get_hub(connection[0], hubs)
            second_hub = Hub.get_hub(connection[1], hubs)
            if first_hub is None or second_hub is None:
                continue

            if first_hub.zone == "blocked":
                color = colors["red"]
            elif first_hub.zone == "priority":
                color = colors["green"]
            elif first_hub.zone == "restricted":
                color = colors["darkred"]
            else:
                color = colors["white"]

            pygame.draw.line(
                window,
                color,
                first_hub.position_on_window,
                second_hub.position_on_window,
                width=3,
            )

    @staticmethod
    def draw_hubs(window: pygame.surface.Surface, hubs: list[Hub]) -> None:
        sidna = pygame.image.load("flags/sidna.jpg")
        sidna = pygame.transform.scale(sidna, (230, 350))
        window.blit(sidna, (0, 650))
        for hub in hubs:
            if hub.color == "none" or hub.color not in colors:
                draw_color = colors["green"]
            else:
                draw_color = colors[hub.color]

            pygame.draw.circle(
                window,
                draw_color,
                (
                    hub.position_on_window[0],
                    hub.position_on_window[1]),
                20,
            )

    @staticmethod
    def draw_frame(
            window: pygame.surface.Surface,
            connections: list[tuple[str, str, int]], hubs: list[Hub],
            start_hub: Hub, target_hub: Hub, drones: list[Drone],
            turn_text: str,
            write_text: Callable[[pygame.surface.Surface, str], None]) -> None:
        window.fill(colors["background"])
        draw_flags(window, start_hub, target_hub)
        Rendring.draw_connections(window, connections, hubs)
        Rendring.draw_hubs(window, hubs)
        write_text(window, turn_text)
        for drone in drones:
            drone.show(
                window, drone.corrent_position[0],
                drone.corrent_position[1])
        pygame.display.update()

    @staticmethod
    def progress_position(
            start: tuple[float, float], end: tuple[float, float],
            progress: float) -> tuple[float, float]:
        return (
            start[0] + (end[0] - start[0]) * progress,
            start[1] + (end[1] - start[1]) * progress,
        )

    @staticmethod
    def draw_turn(
            window: pygame.surface.Surface, clock: pygame.time.Clock,
            connections: list[tuple[str, str, int]], hubs: list[Hub],
            start_hub: Hub, target_hub: Hub, drones: list[Drone],
            write_text: Callable[[pygame.surface.Surface, str], None],
            turn_text: str, movements: list[
                tuple[Drone, tuple[float, float], tuple[float, float]]],
            frames: int = 30) -> bool:

        for frame in range(frames):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()

            progress = frame / frames
            for drone, start_position, end_position in movements:
                drone.corrent_position = Rendring.progress_position(
                    start_position,
                    end_position,
                    progress)

            Rendring.draw_frame(
                window,
                connections,
                hubs,
                start_hub,
                target_hub,
                drones,
                turn_text,
                write_text
            )
            clock.tick(60)

        return True
