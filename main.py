import cv2
import numpy as np
import random
import keyboard

background = cv2.imread('img/background.jpg')
std = cv2.imread('img/std.png', cv2.IMREAD_UNCHANGED)
std = cv2.resize(std, None, fx=1/8, fy=1/8, interpolation=cv2.INTER_AREA)
std_rgb = std[..., :3]
alpha_mask = std[..., 3].astype(float) / 255.0 
garbage = cv2.imread('img/cola.png')
garbage = cv2.resize(garbage, None, fx=2, fy=2, interpolation=cv2.INTER_AREA)
cv2.imshow('Garbage', garbage)

bg_h, bg_w = background.shape[:2]
std_h, std_w = std_rgb.shape[:2]
if (std_h > bg_h or std_w > bg_w):
    scale = min(bg_h/std_h, bg_w/std_w)
    new_w = int(std_w * scale)
    new_h = int(std_h * scale)
    std_rgb = cv2.resize(std_rgb, (new_w, new_h), interpolation=cv2.INTER_AREA)
    alpha_mask = cv2.resize(alpha_mask, (new_w, new_h), interpolation=cv2.INTER_AREA)
    std_h, std_w = new_h, new_w

x, y = 0, 450
step = 3

while True:
    frame = background.copy()

    # 直接在frame上進行alpha混合，不使用roi變數
    for c in range(3):
        frame[y:y+std_h, x:x+std_w, c] = (alpha_mask * std_rgb[..., c] + 
                                         (1 - alpha_mask) * frame[y:y+std_h, x:x+std_w, c]).astype(np.uint8)
    
    cv2.imshow('Move Image with Keyboard', frame)

    if keyboard.is_pressed('q'):
        break
    up    = keyboard.is_pressed('w')   or keyboard.is_pressed('up')
    down  = keyboard.is_pressed('s')   or keyboard.is_pressed('down')
    left  = keyboard.is_pressed('a')   or keyboard.is_pressed('left')
    right = keyboard.is_pressed('d')   or keyboard.is_pressed('right')

    y = max(250, min(bg_h-std_h, y + (down - up)*step))
    x = max(0, min(bg_w-std_w, x + (right - left)*step))

    cv2.waitKey(10)

cv2.destroyAllWindows()




