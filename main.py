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

    garbage_x, garbage_y = random_garbage_pos(view_offset)
    step = 5  # 移动步长
    score = 0
    garbage_visible = True
    garbage_timer = 0

    while True:
        # 创建当前视图窗口
        view_frame = np.zeros((window_height, window_width, 3), dtype=np.uint8)

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

        # 绘制垃圾（如果可见且在当前视窗内）
        if garbage_visible:
            # 计算垃圾在屏幕上的位置
            garbage_screen_x = garbage_x - view_offset
            if 0 <= garbage_screen_x < window_width:
                # 确保不会超出屏幕边界
                visible_x_end = min(window_width, garbage_screen_x + garbage_w)
                visible_width = visible_x_end - garbage_screen_x

                # 确保不会超出底部
                visible_y_end = min(window_height, garbage_y + garbage_h)
                garbage_y_height = visible_y_end - garbage_y

                if visible_width > 0 and garbage_y_height > 0:
                    for c in range(3):
                        view_frame[garbage_y:visible_y_end, garbage_screen_x:visible_x_end, c] = (
                            garbage_alpha[:garbage_y_height, :visible_width] *
                            garbage_rgb[:garbage_y_height, :visible_width, c] +
                            (1 - garbage_alpha[:garbage_y_height, :visible_width]) *
                            view_frame[garbage_y:visible_y_end, garbage_screen_x:visible_x_end, c]
                        ).astype(np.uint8)

        # 绘制角色
        character_y_end = min(window_height, character_y + std_h)
        character_height = character_y_end - character_y

        # 确保角色始终可见，即使靠近屏幕边缘
        character_screen_x = max(0, min(window_width - std_w, character_screen_x))

        if character_height > 0:  # 只要角色高度有效就绘制，移除了对X位置的限制检查
            for c in range(3):
                view_frame[character_y:character_y_end, character_screen_x:character_screen_x+std_w, c] = (
                    alpha_mask[:character_height, :] * std_rgb[:character_height, :, c] +
                    (1 - alpha_mask[:character_height, :]) * view_frame[character_y:character_y_end, character_screen_x:character_screen_x+std_w, c]
                ).astype(np.uint8)

        # 显示分数
        cv2.putText(view_frame, f"Score: {score}", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

        # 移除区域提示文字显示

        # 显示当前视图
        cv2.imshow(window_name, view_frame)

        if keyboard.is_pressed('q'):
            break

        # 处理键盘输入
        up = keyboard.is_pressed('w') or keyboard.is_pressed('up')
        down = keyboard.is_pressed('s') or keyboard.is_pressed('down')
        left = keyboard.is_pressed('a') or keyboard.is_pressed('left')
        right = keyboard.is_pressed('d') or keyboard.is_pressed('right')

        # 上下移动角色
        character_y = max(250, min(window_height - std_h, character_y + (down - up) * step))

        # 左右移动处理
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

        # 碰撞检测
        if garbage_visible:
            garbage_screen_x = garbage_x - view_offset
            if (0 <= garbage_screen_x < window_width and
                abs(character_screen_x + std_w/2 - (garbage_screen_x + garbage_w/2)) < (std_w + garbage_w) / 2 and
                abs(character_y + std_h/2 - (garbage_y + garbage_h/2)) < (std_h + garbage_h) / 2):
                score += 1
                garbage_visible = False
                garbage_timer = cv2.getTickCount()
                ding_sound.play()  # 播放音效

        # 1秒后垃圾再出现
        if not garbage_visible:
            now = cv2.getTickCount()
            elapsed = (now - garbage_timer) / cv2.getTickFrequency()
            if elapsed >= 1.0:
                garbage_x, garbage_y = random_garbage_pos(view_offset)
                garbage_visible = True

        cv2.waitKey(10)


######

# 主程式
window_name = 'Beach Game'
show_menu(window_name)
show_guide(window_name)
beach_game(window_name)
cv2.destroyAllWindows()

# 我們今生注定是倉鼠

