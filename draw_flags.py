import pygame

palistine_frames = [pygame.image.load(f"flags/palestine/ezgif-frame-00{i}.jpg") for i in range(61)]
iran_frames = [pygame.image.load(f"flags/iran/{i}.gif") for i in range(31)]
purk_frames = [pygame.image.load(f"flags/ikhrael/{i}.gif") for i in range(38)]
frame_index_iran = 0
frame_index_purk = 0
frame_delay = 5
counter_iran = 0
counter_purk = 0
counter_palestine = 0
frame_index_palestine = 0

def draw_flags(window, start_hub, target_hub)-> None:
    global frame_index_iran
    global frame_index_purk
    global frame_index_palestine
    global frame_delay
    global counter_iran
    global counter_palestine
    global counter_purk

    counter_palestine += 1
    if counter_palestine >= frame_delay:
        frame_index_palestine = (frame_index_palestine + 1) % 61
        counter_palestine = 0
    img = pygame.transform.scale(palistine_frames[frame_index_palestine], (500, 1000))
    window.blit(
        img,
        (
            600,
            0
        ))

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
