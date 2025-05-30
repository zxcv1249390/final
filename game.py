import cv2
import numpy as np
import random
import keyboard
import pygame
from assets import load_images
import os


def beach_game(window_name):
    # 设置窗口大小
    window_width = 1500
    window_height = 900

    # 加载所有游戏资源
    assets = load_images(window_width, window_height)
    backgrounds = assets['backgrounds']
    recycle_bg = assets['recycle_bg']
    garbage_cans = assets['garbage_cans']
    std_rgb = assets['std_rgb']
    alpha_mask = assets['alpha_mask']
    garbage_rgb = assets['garbage_rgb']
    garbage_alpha = assets['garbage_alpha']
    ding_sound = assets['ding_sound']

    # 获取图像尺寸
    std_h, std_w = std_rgb.shape[:2]
    garbage_h, garbage_w = garbage_rgb.shape[:2]

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
        long_bg[:, i * window_width:(i + 1) * window_width] = bg

    # 调整角色大小
    if std_h > window_height // 3:
        scale = (window_height // 3) / std_h
        new_w = int(std_w * scale)
        new_h = int(std_h * scale)
        std_rgb = cv2.resize(std_rgb, (new_w, new_h), interpolation=cv2.INTER_AREA)
        alpha_mask = cv2.resize(alpha_mask, (new_w, new_h), interpolation=cv2.INTER_AREA)
        std_h, std_w = new_h, new_w

    # 定义随机垃圾位置函数
    def random_garbage_pos(min_x, max_x):
        # 在指定范围内的随机位置
        world_x = random.randint(min_x, max_x - garbage_w)
        y = random.randint(600, window_height - garbage_h - 10)
        return world_x, y

    # 新增垃圾物件類別
    class Garbage:
        def __init__(self, image, x, y):
            self.image = image
            self.x = x
            self.y = y
            self.visible = True

    # 加載垃圾圖片
    garbage_images = []
    garbage_dir = 'img/garbage'
    for filename in os.listdir(garbage_dir):
        if filename.endswith('.png'):
            img_path = os.path.join(garbage_dir, filename)
            garbage_images.append(cv2.imread(img_path, cv2.IMREAD_UNCHANGED))

    # 初始化30个垃圾
    garbage_items = []
    min_dist = 150
    min_dist_sq = min_dist * min_dist
    garbage_count = 35
    # 为每张背景图分配垃圾
    garbage_per_bg = garbage_count // len(backgrounds)
    for bg_idx in range(len(backgrounds)):
        bg_start_x = bg_idx * window_width
        bg_end_x = (bg_idx + 1) * window_width
        for i in range(garbage_per_bg):
            # 生成位置，确保与已有垃圾最小距离
            while True:
                x, y = random_garbage_pos(bg_start_x, bg_end_x)
                if all((x - item.x) ** 2 + (y - item.y) ** 2 >= min_dist_sq for item in garbage_items):
                    break
            garbage_image = random.choice(garbage_images)
            garbage_items.append(Garbage(garbage_image, x, y))

    # 添加剩余的垃圾（如果不能平均分配）
    remaining = garbage_count - (garbage_per_bg * len(backgrounds))
    for i in range(remaining):
        while True:
            x, y = random_garbage_pos(0, total_width)
            if all((x - item.x) ** 2 + (y - item.y) ** 2 >= min_dist_sq for item in garbage_items):
                break
        garbage_image = random.choice(garbage_images)
        garbage_items.append(Garbage(garbage_image, x, y))

    # 定义游戏区域的边界
    free_move_start = 0  # 自由移动开始位置
    fixed_char_start = window_width // 2  # 角色固定位置开始（background1的后半部分）
    fixed_char_end = total_width - window_width // 2  # 角色固定位置结束（background5的前半部分）
    free_move_end = total_width  # 自由移动结束位置

    # 视图偏移量（用于滚动）
    view_offset = 0
    max_view_offset = total_width - window_width  # 最大视图偏移量

    # 角色位置初始化
    character_x = window_width // 4  # 起始位置在第一个区域
    character_y = 600  # 初始Y位置

    # 标记是否进入回收区
    in_recycle_area = False

    # 鼠标位置和垃圾桶悬停状态
    mouse_x, mouse_y = 0, 0
    hovered_can_index = -1

    # 鼠标回调函数
    def mouse_callback(event, x, y, flags, param):
        nonlocal mouse_x, mouse_y
        mouse_x, mouse_y = x, y

    # 注册鼠标回调
    cv2.setMouseCallback(window_name, mouse_callback)

    step = 5  # 移动步长
    score = 0

    while True:
        # 检查是否应该进入回收区
        if view_offset >= max_view_offset and character_x >= window_width - std_w - 10:  # 角色触碰到最右边边界
            in_recycle_area = True
        elif view_offset < max_view_offset - 100:  # 离开最右边一定距离时
            in_recycle_area = False

        # 创建当前视图窗口
        view_frame = np.zeros((window_height, window_width, 3), dtype=np.uint8)

        if in_recycle_area:
            # 显示回收背景
            view_frame[:] = recycle_bg

            # 检查鼠标是否悬停在垃圾桶上
            hovered_can_index = -1
            for i, (x, y) in enumerate(garbage_can_positions):
                gc = garbage_cans[i]
                gc_h, gc_w = gc.shape[:2]

                # 检查鼠标是否在垃圾桶上
                if x <= mouse_x < x + gc_w and y <= mouse_y < y + gc_h:
                    hovered_can_index = i
                    break

            # 绘制垃圾桶
            for i, (x, y) in enumerate(garbage_can_positions):
                gc = garbage_cans[i]
                gc_alpha = gc[..., 3].astype(float) / 255.0

                # 如果是悬停的垃圾桶，稍微放大
                scale_factor = 1.2 if i == hovered_can_index else 1.0
                if scale_factor > 1.0:
                    original_height, original_width = gc.shape[:2]
                    new_width = int(original_width * scale_factor)
                    new_height = int(original_height * scale_factor)
                    resized_gc = cv2.resize(gc, (new_width, new_height), interpolation=cv2.INTER_AREA)

                    # 调整位置，使放大后还居中
                    x_offset = (new_width - original_width) // 2
                    y_offset = (new_height - original_height) // 2
                    x = x - x_offset
                    y = y - y_offset

                    gc = resized_gc
                    gc_alpha = gc[..., 3].astype(float) / 255.0

                gc_h, gc_w = gc.shape[:2]

                # 确保不超出边界
                if x < 0:
                    gc = gc[:, -x:]
                    gc_alpha = gc_alpha[:, -x:]
                    gc_w = gc.shape[1]
                    x = 0

                if y < 0:
                    gc = gc[-y:, :]
                    gc_alpha = gc_alpha[-y:, :]
                    gc_h = gc.shape[0]
                    y = 0

                end_x = min(x + gc_w, window_width)
                end_y = min(y + gc_h, window_height)
                width = end_x - x
                height = end_y - y

                if width > 0 and height > 0:
                    for c in range(3):
                        view_frame[y:end_y, x:end_x, c] = (
                                gc_alpha[:height, :width] * gc[:height, :width, c] +
                                (1 - gc_alpha[:height, :width]) * view_frame[y:end_y, x:end_x, c]
                        ).astype(np.uint8)
        else:
            # 常规游戏区域的绘制
            # 确保视图偏移量不超出范围
            view_offset = max(0, min(view_offset, max_view_offset))

            # 从长背景中截取当前视图
            view_frame[:] = long_bg[:, view_offset:view_offset + window_width]

            # 根据角色的世界坐标计算屏幕坐标
            character_world_x = view_offset + character_x

            # 判断角色当前所在区域，调整角色屏幕位置和视图偏移量
            if character_world_x < fixed_char_start:
                # 区域1：自由移动区（背景1的前半部分）
                character_screen_x = character_x
                # 确保视图保持在起始位置
                view_offset = 0
            elif character_world_x >= fixed_char_end:
                # 区域3：自由移动区（背景5的后半部分）
                view_offset = max_view_offset
                character_screen_x = character_world_x - view_offset
            else:
                # 区域2：角色固定在屏幕中央，背景滚动
                character_screen_x = window_width // 2
                view_offset = character_world_x - character_screen_x

            # 绘制所有可见的垃圾
            for garbage_item in garbage_items:
                if garbage_item.visible:
                    # 确保每個垃圾物件使用其自身的圖片和透明度通道進行渲染
                    garbage_image = garbage_item.image
                    garbage_alpha = garbage_image[:, :, 3] / 255.0  # 提取 alpha 通道
                    garbage_rgb = garbage_image[:, :, :3]  # 提取 RGB 通道

                    # 计算垃圾在屏幕上的位置
                    garbage_screen_x = garbage_item.x - view_offset
                    garbage_y = garbage_item.y

                    # 只绘制在当前视窗内的垃圾
                    if -garbage_image.shape[1] < garbage_screen_x < window_width:
                        # 确保不会超出屏幕边界
                        visible_x_start = max(0, garbage_screen_x)
                        garbage_x_offset = visible_x_start - garbage_screen_x
                        visible_x_end = min(window_width, garbage_screen_x + garbage_image.shape[1])
                        visible_width = visible_x_end - visible_x_start

                        # 确保不会超出底部
                        visible_y_end = min(window_height, garbage_y + garbage_image.shape[0])
                        garbage_y_height = visible_y_end - garbage_y

                        if visible_width > 0 and garbage_y_height > 0:
                            for c in range(3):
                                view_frame[garbage_y:visible_y_end, visible_x_start:visible_x_end, c] = (
                                    garbage_alpha[:garbage_y_height, garbage_x_offset:garbage_x_offset + visible_width] *
                                    garbage_rgb[:garbage_y_height, garbage_x_offset:garbage_x_offset + visible_width, c] +
                                    (1 - garbage_alpha[:garbage_y_height, garbage_x_offset:garbage_x_offset + visible_width]) *
                                    view_frame[garbage_y:visible_y_end, visible_x_start:visible_x_end, c]
                                ).astype(np.uint8)

            # 绘制角色
            character_y_end = min(window_height, character_y + std_h)
            character_height = character_y_end - character_y

            # 确保角色始终可见，即使靠近屏幕边缘
            character_screen_x = max(0, min(window_width - std_w, character_screen_x))

            if character_height > 0:  # 只要角色高度有效就绘制，移除了对X位置的限制检查
                for c in range(3):
                    view_frame[character_y:character_y_end, character_screen_x:character_screen_x + std_w, c] = (
                            alpha_mask[:character_height, :] * std_rgb[:character_height, :, c] +
                            (1 - alpha_mask[:character_height, :]) * view_frame[character_y:character_y_end,
                                                                     character_screen_x:character_screen_x + std_w, c]
                    ).astype(np.uint8)

        # 显示分数
        cv2.putText(view_frame, f"Score: {score}", (40, 120), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4, cv2.LINE_AA)

        # 显示当前视图
        cv2.imshow(window_name, view_frame)

        key = cv2.waitKey(10)
        if keyboard.is_pressed('q') or key == 27:  # ESC键或q退出
            break

        # 处理键盘输入
        up = keyboard.is_pressed('w') or keyboard.is_pressed('up')
        down = keyboard.is_pressed('s') or keyboard.is_pressed('down')
        left = keyboard.is_pressed('a') or keyboard.is_pressed('left')
        right = keyboard.is_pressed('d') or keyboard.is_pressed('right')

        # 上下移动角色
        character_y = max(430, min(window_height - std_h, character_y + (down - up) * step))

        # 左右移动处理（只在非回收区时）
        if not in_recycle_area:
            if left:
                character_world_x = max(0, character_world_x - step)
            if right:
                character_world_x = min(total_width - std_w, character_world_x + step)

            # 根据新的世界坐标更新角色的屏幕坐标和视图偏移量
            if character_world_x < fixed_char_start:
                # 区域1
                character_x = character_world_x
                view_offset = 0
            elif character_world_x >= fixed_char_end:
                # 区域3
                view_offset = max_view_offset
                character_x = character_world_x - view_offset
            else:
                # 区域2
                character_x = window_width // 2
                view_offset = character_world_x - character_x
        else:
            # 在回收区时，按左键可以返回游戏区
            if left:
                in_recycle_area = False
                view_offset = max_view_offset - 100

        # 碰撞检测（只在非回收区时）
        if not in_recycle_area:
            for idx, garbage_item in enumerate(garbage_items):
                if garbage_item.visible:
                    garbage_screen_x = garbage_item.x - view_offset
                    garbage_y = garbage_item.y

                    # 只检测在当前视窗内的垃圾
                    if -garbage_w < garbage_screen_x < window_width:
                        if (abs(character_screen_x + std_w / 2 - (garbage_screen_x + garbage_w / 2)) < (
                                std_w + garbage_w) / 2 and
                                abs(character_y + std_h / 2 - (garbage_y + garbage_h / 2)) < (std_h + garbage_h) / 2):
                            score += 1
                            garbage_items[idx].visible = False
                            ding_sound.play()  # 播放音效
                            break  # 每帧只处理一个碰撞