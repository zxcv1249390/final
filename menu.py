import cv2
import numpy as np
import keyboard
import time
import pygame

WINDOW_WIDTH = 1500
WINDOW_HEIGHT = 900

def wait_for_key_release(keys):
    """等待指定鍵都釋放後才繼續"""
    while any(keyboard.is_pressed(k) for k in keys):
        cv2.waitKey(10)

def show_menu(window_name):
    pygame.mixer.init()
    button_sound = pygame.mixer.Sound('sound/button.wav') # Renamed variable for clarity
        
    background = cv2.imread('background/background1.jpg')
    if background is not None:
        background = cv2.resize(background, (WINDOW_WIDTH, WINDOW_HEIGHT))
    else:
        background = np.full((WINDOW_HEIGHT, WINDOW_WIDTH, 3), (0, 128, 255), dtype=np.uint8)

    menu_img = cv2.imread('img/beach.png')
    if menu_img is not None:
        menu_img = cv2.resize(menu_img, (WINDOW_WIDTH, WINDOW_HEIGHT))
        menu_bg = menu_img
    else:
        menu_bg = background
        cv2.putText(menu_bg, 'Beach Game', (WINDOW_WIDTH//2-200, WINDOW_HEIGHT//2),
                            cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 255, 255), 3)
        cv2.putText(menu_bg, 'Press SPACE to start', (WINDOW_WIDTH//2-250, WINDOW_HEIGHT//2+100),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    cv2.imshow(window_name, menu_bg)
    cv2.waitKey(1)

    # 等候開始
    while True:
        if keyboard.is_pressed('space') or keyboard.is_pressed('enter'):
            button_sound.play() # Play sound when space or enter is pressed
            wait_for_key_release(['space', 'enter'])
            break
        if keyboard.is_pressed('q') or keyboard.is_pressed('esc'):
            exit()
        cv2.waitKey(10)

    # 說明頁邏輯
    instruction_pages = ['img/2.png', 'img/3.png', 'img/4.png']
    page_index = 0
    total_pages = len(instruction_pages)

    while True:
        page_img = cv2.imread(instruction_pages[page_index])
        if page_img is not None:
            page_img = cv2.resize(page_img, (WINDOW_WIDTH, WINDOW_HEIGHT))
        else:
            page_img = background.copy()
            cv2.putText(page_img, f'Page {page_index + 1}', (100, 100),
                                    cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)

        cv2.imshow(window_name, page_img)
        cv2.waitKey(1)

        if keyboard.is_pressed('space') or keyboard.is_pressed('enter'):
            button_sound.play() # Play sound when space or enter is pressed
            wait_for_key_release(['space', 'enter'])
            break
        
        if keyboard.is_pressed('d') or keyboard.is_pressed('right'):
            button_sound.play() # Play sound when 'd' or 'right' is pressed
            page_index = (page_index + 1) % total_pages
            wait_for_key_release(['d', 'right'])

        if keyboard.is_pressed('q') or keyboard.is_pressed('esc'):
            exit()

        cv2.waitKey(10)