import cv2
import numpy as np
import keyboard

WINDOW_WIDTH = 1500
WINDOW_HEIGHT = 900

def show_menu(window_name):
    # 載入背景
    background = cv2.imread('background/background1.jpg')
    if background is not None:
        background = cv2.resize(background, (WINDOW_WIDTH, WINDOW_HEIGHT))
    else:
        background = np.full((WINDOW_HEIGHT, WINDOW_WIDTH, 3), (0, 128, 255), dtype=np.uint8)
    
    # 載入選單圖片
    menu_img = cv2.imread('img/beach.png')
    if menu_img is not None:
        menu_img = cv2.resize(menu_img, (WINDOW_WIDTH, WINDOW_HEIGHT))
        menu_bg = menu_img
    else:
        menu_bg = background
        # 在背景上添加文字
        cv2.putText(menu_bg, 'Beach Game', (WINDOW_WIDTH//2-200, WINDOW_HEIGHT//2), 
                   cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 255, 255), 3)
        cv2.putText(menu_bg, 'Press SPACE to start', (WINDOW_WIDTH//2-250, WINDOW_HEIGHT//2+100), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    cv2.imshow(window_name, menu_bg)
    cv2.waitKey(1)

    while True:
        if keyboard.is_pressed('space') or keyboard.is_pressed('enter'):
            break
        if keyboard.is_pressed('q') or keyboard.is_pressed('esc'):
            exit()
        cv2.waitKey(10)