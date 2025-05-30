import cv2
import numpy as np
import keyboard
import pygame

WINDOW_WIDTH = 1500
WINDOW_HEIGHT = 900

# 初始化音效
pygame.mixer.init()
button_sound = pygame.mixer.Sound('sound/button.wav')


def show_menu(window_name):
    background = cv2.imread('background/background1.jpg')
    menu_img = cv2.imread('img/beach.png')

    background = cv2.resize(background, (WINDOW_WIDTH, WINDOW_HEIGHT), interpolation=cv2.INTER_AREA)
    menu_img = cv2.resize(menu_img, (WINDOW_WIDTH, WINDOW_HEIGHT), interpolation=cv2.INTER_AREA)

    menu_bg = background.copy()
    if menu_img.shape[2] == 4:
        alpha = menu_img[..., 3] / 255.0
        for c in range(3):
            menu_bg[..., c] = (alpha * menu_img[..., c] + (1 - alpha) * menu_bg[..., c]).astype(np.uint8)
    else:
        menu_bg = menu_img
    cv2.imshow(window_name, menu_bg)
    cv2.waitKey(1)

    while True:
        if keyboard.is_pressed('space') or keyboard.is_pressed('enter'):
            button_sound.play()  # ▶ 播放音效
            break
        if keyboard.is_pressed('q'):
            exit()
        cv2.waitKey(10)


def show_guide(window_name):
    while keyboard.is_pressed('space') or keyboard.is_pressed('enter') or keyboard.is_pressed(
            'right') or keyboard.is_pressed('d'):
        cv2.waitKey(10)

    guide_imgs = [
        cv2.imread('img/2.png'),
        cv2.imread('img/3.png'),
        cv2.imread('img/4.png')
    ]
    guide_imgs = [cv2.resize(img, (WINDOW_WIDTH, WINDOW_HEIGHT), interpolation=cv2.INTER_AREA) for img in guide_imgs]
    idx = 0

    while True:
        cv2.imshow(window_name, guide_imgs[idx])
        cv2.waitKey(1)
        if keyboard.is_pressed('right') or keyboard.is_pressed('d'):
            idx = (idx + 1) % 3
            button_sound.play()  # ▶ 播放音效
            while keyboard.is_pressed('right') or keyboard.is_pressed('d'):
                cv2.waitKey(10)
        if keyboard.is_pressed('space') or keyboard.is_pressed('enter'):
            button_sound.play()  # ▶ 播放音效
            break
        if keyboard.is_pressed('q'):
            exit()
        cv2.waitKey(10)
