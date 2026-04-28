import pygame
from classes import Hub

iran_frames = [pygame.image.load(f"flags/iran/{i}.gif") for i in range(31)]
purk_frames = [pygame.image.load(f"flags/ikhrael/{i}.gif") for i in range(38)]
frame_index_iran = 0
frame_index_purk = 0
counter_iran = 0
counter_purk = 0


def draw_flags(
        window: pygame.surface.Surface,
        start_hub: Hub, target_hub: Hub) -> None:
    global frame_index_iran
    global frame_index_purk
    global counter_iran
    global counter_purk
    frame_delay = 5

    counter_iran += 1
    if counter_iran >= frame_delay:
        frame_index_iran = (frame_index_iran + 1) % 31
        counter_iran = 0
    img = pygame.transform.scale(iran_frames[frame_index_iran], (100, 70))
    window.blit(
        img,
        (
            start_hub.position_on_window[0] - 50,
            start_hub.position_on_window[1] - 100
        ))

    counter_purk += 1
    if counter_purk >= frame_delay:
        frame_index_purk = (frame_index_purk + 1) % 37
        counter_purk = 0
    img = pygame.transform.scale(purk_frames[frame_index_purk], (150, 100))
    window.blit(
        img,
        (
            target_hub.position_on_window[0] - 60,
            target_hub.position_on_window[1] - 120
        ))
