import cv2
import numpy as np
import random
import keyboard
import pygame


def show_menu(window_name):
    background = cv2.imread('background/background1.jpg')
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
    while keyboard.is_pressed('space') or keyboard.is_pressed('enter') or keyboard.is_pressed(
            'right') or keyboard.is_pressed('d'):
        cv2.waitKey(10)
    guide_imgs = [
        cv2.imread('img/guide.png'),
        cv2.imread('img/guide2.png'),
        cv2.imread('img/guide3.png')
    ]
    bg = cv2.imread('background/background1.jpg')
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
    # 设置窗口大小
    window_width = 800
    window_height = 600

    # 加载所有背景图片
    backgrounds = []
    for i in range(1, 6):  # 加载背景1到背景5
        bg = cv2.imread(f'background/background{i}.jpg')
        if bg is not None:
            # 确保所有背景图片都调整为相同的大小
            bg = cv2.resize(bg, (window_width, window_height), interpolation=cv2.INTER_AREA)
            backgrounds.append(bg)

    # 如果没有成功加载任何背景图片，创建一个默认背景
    if len(backgrounds) == 0:
        default_bg = np.zeros((window_height, window_width, 3), dtype=np.uint8)
        default_bg[:] = (0, 128, 255)  # 创建蓝色背景
        backgrounds = [default_bg]

    # 加载回收背景
    recycle_bg = cv2.imread('background/recycle_background.jpg')
    if recycle_bg is not None:
        recycle_bg = cv2.resize(recycle_bg, (window_width, window_height), interpolation=cv2.INTER_AREA)
    else:
        recycle_bg = np.zeros((window_height, window_width, 3), dtype=np.uint8)
        recycle_bg[:] = (0, 200, 100)  # 创建默认回收背景

    # 加载垃圾桶图片
    garbage_cans = []
    for i in range(1, 5):  # 加载垃圾桶1到垃圾桶4
        gc = cv2.imread(f'img/garbage_can/garbage_can{i}.png', cv2.IMREAD_UNCHANGED)
        if gc is not None:
            # 调整大小为合适尺寸
            gc = cv2.resize(gc, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
            garbage_cans.append(gc)

    # 计算垃圾桶的位置（均匀分布在回收背景的中间区域）
    garbage_can_positions = []
    if garbage_cans:
        gc_height = garbage_cans[0].shape[0]
        gc_width = garbage_cans[0].shape[1]
        spacing = window_width // (len(garbage_cans) + 1)

        for i in range(len(garbage_cans)):
            x = spacing * (i + 1) - gc_width // 2
            y = window_height // 2 - gc_height // 2
            garbage_can_positions.append((x, y))

    # 创建长背景（拼接五张图片）
    total_width = window_width * len(backgrounds)
    long_bg = np.zeros((window_height, total_width, 3), dtype=np.uint8)
    for i, bg in enumerate(backgrounds):
        long_bg[:, i*window_width:(i+1)*window_width] = bg

    # 加载角色和垃圾图像
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

    # 获取图像尺寸
    bg_h, bg_w = window_height, total_width
    std_h, std_w = std_rgb.shape[:2]
    garbage_h, garbage_w = garbage_rgb.shape[:2]

    # 调整角色大小
    if std_h > window_height // 3:
        scale = (window_height // 3) / std_h
        new_w = int(std_w * scale)
        new_h = int(std_h * scale)
        std_rgb = cv2.resize(std_rgb, (new_w, new_h), interpolation=cv2.INTER_AREA)
        alpha_mask = cv2.resize(alpha_mask, (new_w, new_h), interpolation=cv2.INTER_AREA)
        std_h, std_w = new_h, new_w

    # 定义随机垃圾位置函数
    def random_garbage_pos(view_offset):
        # 在可见范围内的随机位置
        screen_x = random.randint(50, window_width - garbage_w - 50)
        world_x = min(total_width - garbage_w, screen_x + view_offset)
        y = random.randint(400, window_height - garbage_h - 10)
        return world_x, y

    # 定义游戏区域的边界
    free_move_start = 0                            # 自由移动开始位置
    fixed_char_start = window_width // 2           # 角色固定位置开始（background1的后半部分）
    fixed_char_end = total_width - window_width // 2  # 角色固定位置结束（background5的前半部分）
    free_move_end = total_width                    # 自由移动结束位置

    # 视图偏移量（用于滚动）
    view_offset = 0
    max_view_offset = total_width - window_width  # 最大视图偏移量

    # 角色位置初始化
    character_x = window_width // 4  # 起始位置在第一个区域
    character_y = 300  # 初始Y位置

    # 标记是否进入回收区
    in_recycle_area = False

    # 鼠标位置和垃圾桶悬停状态
    mouse_x, mouse_y =
