import cv2
import numpy as np
import random
import keyboard
import pygame

def show_menu(window_name):
    background = cv2.imread('img/background.jpg')
    menu_img = cv2.imread('img/menu.png')
    bg_h, bg_w = background.shape[:2]
    menu_img = cv2.resize(menu_img, (bg_w, bg_h), interpolation=cv2.INTER_AREA)
    menu_bg = background.copy()
    if menu_img.shape[2] == 4:
        alpha = menu_img[..., 3] / 255.0
        for c in range(3):
            menu_bg[..., c] = (alpha * menu_img[..., c] + (1 - alpha) * menu_bg[..., c]).astype(np.uint8)
    else:
        menu_bg = menu_img
    cv2.imshow(window_name, menu_bg)
    cv2.waitKey(1)
    # 等待玩家按下任意鍵開始
    while True:
        if keyboard.is_pressed('space') or keyboard.is_pressed('enter'):
            break
        if keyboard.is_pressed('q'):
            exit()
        cv2.waitKey(10)

def show_guide(window_name):
    # 等待玩家放開所有按鍵，避免殘留按鍵直接觸發
    while keyboard.is_pressed('space') or keyboard.is_pressed('enter') or keyboard.is_pressed('right') or keyboard.is_pressed('d'):
        cv2.waitKey(10)
    guide_imgs = [
        cv2.imread('img/guide.png'),
        cv2.imread('img/guide2.png'),
        cv2.imread('img/guide3.png')
    ]
    bg = cv2.imread('img/background.jpg')
    bg_h, bg_w = bg.shape[:2]
    guide_imgs = [cv2.resize(img, (bg_w, bg_h), interpolation=cv2.INTER_AREA) for img in guide_imgs]
    idx = 0
    while True:
        cv2.imshow(window_name, guide_imgs[idx])
        cv2.waitKey(1)
        if keyboard.is_pressed('right') or keyboard.is_pressed('d'):
            idx = (idx + 1) % 3
            while keyboard.is_pressed('right') or keyboard.is_pressed('d'):
                cv2.waitKey(10)
        if keyboard.is_pressed('space') or keyboard.is_pressed('enter'):
            break
        if keyboard.is_pressed('q'):
            exit()
        cv2.waitKey(10)
        
######
        
def beach_game(window_name):
    background = cv2.imread('img/background.jpg')
    std = cv2.imread('img/std.png', cv2.IMREAD_UNCHANGED)
    std = cv2.resize(std, None, fx=1/8, fy=1/8, interpolation=cv2.INTER_AREA)
    std_rgb = std[..., :3]
    alpha_mask = std[..., 3].astype(float) / 255.0 
    garbage = cv2.imread('img/cola.png', cv2.IMREAD_UNCHANGED)
    garbage = cv2.resize(garbage, None, fx=1, fy=1, interpolation=cv2.INTER_AREA)
    garbage_rgb = garbage[..., :3]
    garbage_alpha = garbage[..., 3].astype(float) / 255.0

    # 初始化pygame mixer
    pygame.mixer.init()
    ding_sound = pygame.mixer.Sound('sound/ding.wav')

    bg_h, bg_w = background.shape[:2]
    std_h, std_w = std_rgb.shape[:2]
    garbage_h, garbage_w = garbage_rgb.shape[:2]
    if (std_h > bg_h or std_w > bg_w):
        scale = min(bg_h/std_h, bg_w/std_w)
        new_w = int(std_w * scale)
        new_h = int(std_h * scale)
        std_rgb = cv2.resize(std_rgb, (new_w, new_h), interpolation=cv2.INTER_AREA)
        alpha_mask = cv2.resize(alpha_mask, (new_w, new_h), interpolation=cv2.INTER_AREA)
        std_h, std_w = new_h, new_w

    def random_garbage_pos():
        x = random.randint(0, bg_w - garbage_w)
        y = random.randint(400, bg_h - garbage_h)
        return x, y

    garbage_x, garbage_y = random_garbage_pos()
    x, y = 0, 450
    step = 3
    score = 0
    garbage_visible = True
    garbage_timer = 0

    while True:
        frame = background.copy()
        # 畫垃圾
        if garbage_visible:
            for c in range(3):
                frame[garbage_y:garbage_y+garbage_h, garbage_x:garbage_x+garbage_w, c] = (
                    garbage_alpha * garbage_rgb[..., c] +
                    (1 - garbage_alpha) * frame[garbage_y:garbage_y+garbage_h, garbage_x:garbage_x+garbage_w, c]
                ).astype(np.uint8)
        # 畫角色
        for c in range(3):
            frame[y:y+std_h, x:x+std_w, c] = (
                alpha_mask * std_rgb[..., c] +
                (1 - alpha_mask) * frame[y:y+std_h, x:x+std_w, c]
            ).astype(np.uint8)
        # 顯示分數
        cv2.putText(frame, f"Score: {score}", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,255), 4, cv2.LINE_AA)
        
        cv2.imshow(window_name, frame)

        if keyboard.is_pressed('q'):
            break
        up    = keyboard.is_pressed('w')   or keyboard.is_pressed('up')
        down  = keyboard.is_pressed('s')   or keyboard.is_pressed('down')
        left  = keyboard.is_pressed('a')   or keyboard.is_pressed('left')
        right = keyboard.is_pressed('d')   or keyboard.is_pressed('right')

        y = max(250, min(bg_h-std_h, y + (down - up)*step))
        x = max(0, min(bg_w-std_w, x + (right - left)*step))

        # 碰撞偵測
        if garbage_visible:
            if (x < garbage_x + garbage_w and x + std_w > garbage_x and
                y < garbage_y + garbage_h and y + std_h > garbage_y):
                score += 1
                garbage_visible = False
                garbage_timer = cv2.getTickCount()
                ding_sound.play()  # 播放音效

        # 1秒後垃圾再出現
        if not garbage_visible:
            now = cv2.getTickCount()
            elapsed = (now - garbage_timer) / cv2.getTickFrequency()
            if elapsed >= 1.0:
                garbage_x, garbage_y = random_garbage_pos()
                garbage_visible = True

        cv2.waitKey(10)
        
######

# 主程式
window_name = 'Beach Game'
show_menu(window_name)
show_guide(window_name)
beach_game(window_name)
cv2.destroyAllWindows()

#我們今生注定是倉鼠