from __future__ import annotations

import pygame

from draw_flags import draw_flags
from classes import Hub
from some_parameters import colors


class Rendring:
    @staticmethod
    def lerp_position(start: tuple[float, float], end: tuple[float, float], progress: float) -> tuple[float, float]:
        return (
            start[0] + (end[0] - start[0]) * progress,
            start[1] + (end[1] - start[1]) * progress,
        )

    @staticmethod
    def draw_connections(window, connections, hubs):
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
    def draw_hubs(window, hubs):
        for hub in hubs:
            if hub.color == "none" or hub.color not in colors:
                draw_color = colors["green"]
            else:
                draw_color = colors[hub.color]

            pygame.draw.circle(
                window,
                draw_color,
                (int(hub.position_on_window[0]), int(hub.position_on_window[1])),
                20,
            )

    @staticmethod
    def draw_scene(window, connections, hubs, start_hub, target_hub, drones, turn_text, write_text):
        window.fill(colors["background"])
        Rendring.draw_connections(window, connections, hubs)
        Rendring.draw_hubs(window, hubs)
        for _ in range(10):
            draw_flags(window, start_hub, target_hub)
        write_text(window, turn_text)
        for drone in drones:
            drone.show(window, drone.display_position[0], drone.display_position[1])
        pygame.display.update()

    @staticmethod
    def animate_movements(
        window,
        clock,
        connections,
        hubs,
        start_hub,
        target_hub,
        drones,
        write_text,
        turn_text,
        movements,
        frames: int = 12,
    ):
        for frame in range(1, frames + 1):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    raise SystemExit

            progress = frame / frames
            for drone, start_position, end_position in movements:
                drone.display_position = Rendring.lerp_position(
                    start_position,
                    end_position,
                    progress,
                )

            Rendring.draw_scene(
                window,
                connections,
                hubs,
                start_hub,
                target_hub,
                drones,
                turn_text,
                write_text,
            )
            clock.tick(60)

        for drone, _, end_position in movements:
            drone.display_position = end_position

        return True