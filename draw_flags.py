import pygame

iran_frames = [pygame.image.load(f"flags/iran/{i}.gif") for i in range(31)]
purk_frames = [pygame.image.load(f"flags/ikhrael/ezgif-frame-0{i}.jpg") for i in range(37)]
frame_index_iran = 0
frame_index_purk = 0
frame_delay_iran = 30
frame_delay_purk = 36
counter_iran = 0
counter_purk = 0

def draw_flags(window, start_hub, target_hub):
    global frame_index_iran
    global frame_index_purk
    global frame_delay_iran
    global frame_delay_purk
    global counter_iran
    global counter_purk
    counter_iran += 1
    if counter_iran >= frame_delay_iran:
        frame_index_iran = (frame_index_iran + 1) % len(iran_frames)
        counter_iran = 0
    img = pygame.transform.scale(iran_frames[frame_index_iran], (100, 70))
    window.blit(
        img,
        (
            start_hub.position_on_window[0] - 50,
            start_hub.position_on_window[1] - 100
        ))
    counter_purk += 1
    if counter_purk >= frame_delay_purk:
        frame_index_purk = (frame_index_purk + 1) % len(purk_frames)
        counter_purk = 0
    img = pygame.transform.scale(purk_frames[frame_index_purk], (100, 70))
    window.blit(
        img,
        (
            target_hub.position_on_window[0] - 50,
            target_hub.position_on_window[1] - 100
        ))
