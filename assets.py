import cv2
import numpy as np
import pygame


def load_images(window_width, window_height):
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

    # 加载角色和垃圾图像
    std = cv2.imread('img/std.png', cv2.IMREAD_UNCHANGED)
    std = cv2.resize(std, None, fx=1 / 8, fy=1 / 8, interpolation=cv2.INTER_AREA)
    std_rgb = std[..., :3]
    alpha_mask = std[..., 3].astype(float) / 255.0

    garbage = cv2.imread('img/garbage/cola.png', cv2.IMREAD_UNCHANGED)
    garbage = cv2.resize(garbage, None, fx=1, fy=1, interpolation=cv2.INTER_AREA)
    garbage_rgb = garbage[..., :3]
    garbage_alpha = garbage[..., 3].astype(float) / 255.0

    # 初始化pygame mixer
    pygame.mixer.init()
    ding_sound = pygame.mixer.Sound('sound/ding.wav')

    return {
        'backgrounds': backgrounds,
        'recycle_bg': recycle_bg,
        'garbage_cans': garbage_cans,
        'std_rgb': std_rgb,
        'alpha_mask': alpha_mask,
        'garbage_rgb': garbage_rgb,
        'garbage_alpha': garbage_alpha,
        'ding_sound': ding_sound
    }