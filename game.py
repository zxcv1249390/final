import cv2
import numpy as np
import random
import keyboard
import os
import pygame

def load_images(window_width, window_height):
    # 載入背景圖片
    backgrounds = []
    for i in range(1, 6):
        bg = cv2.imread(f'background/background{i}.jpg')
        if bg is not None:
            bg = cv2.resize(bg, (1350, 810))
            backgrounds.append(bg)
    
    # 如果沒有背景圖片，創建預設背景
    if not backgrounds:
        default_bg = np.full((window_height, window_width, 3), (0, 128, 255), dtype=np.uint8)
        backgrounds = [default_bg]

    # 載入回收背景
    recycle_bg = cv2.imread('background/recycle_background.jpg')
    if recycle_bg is not None:
        recycle_bg = cv2.resize(recycle_bg, (window_width, window_height))
    else:
        recycle_bg = np.full((window_height, window_width, 3), (0, 200, 100), dtype=np.uint8)

    # 載入角色動畫圖像 - 向右走
    std_frames_right = []
    print("開始載入向右走的圖片...")
    for i in range(1, 13):  # 載入1.png到12.png
        frame_path = f'img/std_moving_right/{i}.png'
        print(f"嘗試載入：{frame_path}")
        frame = cv2.imread(frame_path, cv2.IMREAD_UNCHANGED)
        if frame is not None:
            print(f"成功載入第 {i} 幀")
            frame_rgb = frame[..., :3]
            frame_alpha = frame[..., 3].astype(float) / 255.0
            std_frames_right.append((frame_rgb, frame_alpha))
        else:
            print(f"無法載入第 {i} 幀")

    # 載入角色動畫圖像 - 向左走
    std_frames_left = []
    for i in range(1, 13):  # 載入1.png到12.png
        frame = cv2.imread(f'img/std_moving_left/{i}.png', cv2.IMREAD_UNCHANGED)
        if frame is not None:
            frame_rgb = frame[..., :3]
            frame_alpha = frame[..., 3].astype(float) / 255.0
            std_frames_left.append((frame_rgb, frame_alpha))
    
    # 載入角色動畫圖像 - 向右走
    std_frames_right = []
    for i in range(1, 13):  # 載入1.png到12.png
        frame = cv2.imread(f'img/std_moving_right/{i}.png', cv2.IMREAD_UNCHANGED)
        if frame is not None:
            frame_rgb = frame[..., :3]
            frame_alpha = frame[..., 3].astype(float) / 255.0
            std_frames_right.append((frame_rgb, frame_alpha))
    
    # 如果沒有成功載入任何左側圖像，創建預設角色
    if not std_frames_left:
        default_rgb = np.full((50, 40, 3), (255, 0, 0), dtype=np.uint8)
        default_alpha = np.ones((50, 40), dtype=float)
        std_frames_left = [(default_rgb, default_alpha)]
    
    # 如果沒有成功載入任何右側圖像，創建預設角色
    if not std_frames_right:
        default_rgb = np.full((50, 40, 3), (255, 0, 0), dtype=np.uint8)
        default_alpha = np.ones((50, 40), dtype=float)
        std_frames_right = [(default_rgb, default_alpha)]
    
    # 設定初始幀
    std_rgb, alpha_mask = std_frames_left[0]

    # 載入垃圾圖像
    garbage = cv2.imread('img/garbage/cola.png', cv2.IMREAD_UNCHANGED)
    if garbage is not None:
        garbage = cv2.resize(garbage, None, fx=0.5, fy=0.5)
    else:
        # 創建預設垃圾
        garbage = np.full((30, 20, 4), (0, 255, 0, 255), dtype=np.uint8)

    # 初始化音效
    try:
        pygame.mixer.init()
        ding_sound = pygame.mixer.Sound('sound/ding.wav')
        wrong_sound = pygame.mixer.Sound('sound/wrong.wav')
    except:
        ding_sound = None
        wrong_sound = None

    return {
        'backgrounds': backgrounds,
        'recycle_bg': recycle_bg,
        'std_rgb': std_rgb,
        'alpha_mask': alpha_mask,
        'std_frames_left': std_frames_left,
        'std_frames_right': std_frames_right,
        'garbage_image': garbage,
        'ding_sound': ding_sound,
        'wrong_sound': wrong_sound
    }

    
class Garbage:
    def __init__(self, image, x, y, garbage_type="一般"):
        self.image = image
        self.x = x
        self.y = y
        self.visible = True
        self.garbage_type = garbage_type  # 增加垃圾類型屬性

def beach_game(window_name):
    window_width = 1350
    window_height = 810
    
    # 載入資源
    assets = load_images(window_width, window_height)
    backgrounds = assets['backgrounds']
    recycle_bg = assets['recycle_bg']
    std_rgb = assets['std_rgb']
    alpha_mask = assets['alpha_mask']
    std_frames_left = assets['std_frames_left']  # 向左走的動畫幀
    std_frames_right = assets['std_frames_right']  # 向右走的動畫幀
    ding_sound = assets['ding_sound']
    wrong_sound = assets['wrong_sound']
    
    # 預先載入所有回收區背景圖片
    recycle_backgrounds = {
        'default': cv2.imread('recycle_background/garbage_can_close.jpg'),
        'other_open': cv2.imread('recycle_background/other_open.jpg'),
        'garbage_open': cv2.imread('recycle_background/garbage_open.jpg'),
        'paper_open': cv2.imread('recycle_background/paper_open.jpg'),
        'iron_open': cv2.imread('recycle_background/iron_open.jpg')
    }

    # 載入固定的回收區角色圖片
    recycle_std_img = cv2.imread('recycle_background/std.png', cv2.IMREAD_UNCHANGED)
    if recycle_std_img is None:
        recycle_std_img = np.full((100, 80, 4), (255, 0, 0, 255), dtype=np.uint8)

    # 載入指定的垃圾桶特寫背景
    recycle_custom_bg = cv2.imread('recycle_background/garbage_can_close.jpg')
    if recycle_custom_bg is not None:
        recycle_custom_bg = cv2.resize(recycle_custom_bg, (window_width, window_height))
    else:
        # 如果無法載入指定背景，則使用預設背景
        recycle_custom_bg = recycle_bg
        
    # 載入其他垃圾桶打開的背景
    other_open_bg = cv2.imread('recycle_background/other_open.jpg')
    if other_open_bg is not None:
        other_open_bg = cv2.resize(other_open_bg, (window_width, window_height))
    else:
        # 如果無法載入，使用預設背景
        other_open_bg = recycle_custom_bg

    # 角色尺寸
    std_h, std_w = std_rgb.shape[:2]

    # 定義垃圾矩陣
    garbage_matrix = [
        {"file": "bottle_01.png", "type": "other"},
        {"file": "box.png", "type": "paper"},
        {"file": "chips.png", "type": "garbage"},
        {"file": "cola.png", "type": "iron"},
        {"file": "garbage_bag_01.png", "type": "garbage"},
        {"file": "Mai_box.png", "type": "papre"},
        {"file": "milk_box.png", "type": "paper"},
        {"file": "pepsi_can.png", "type": "iron"},
        {"file": "straw_01.png", "type": "garbage"},
        {"file": "tissue_01.png", "type": "garbage"},
        {"file": "shell_01.png", "type": "shell"},
        {"file": "shell_02.png", "type": "sgell"}
    ]

    # 載入所有垃圾圖像
    garbage_images = {}
    for item in garbage_matrix:
        img_path = f'img/garbage/{item["file"]}'
        if os.path.exists(img_path):
            img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
            if img is not None:
                img = cv2.resize(img, None, fx=0.8, fy=0.8)
                garbage_images[item["file"]] = img
        
    # 如果沒有成功載入任何垃圾圖像，創建一個預設垃圾
    if not garbage_images:
        default_garbage = np.full((30, 20, 4), (0, 255, 0, 255), dtype=np.uint8)
        garbage_images["default.png"] = default_garbage
        garbage_matrix = [{"file": "default.png", "type": "一般"}]


    # 創建長背景
    total_width = window_width * len(backgrounds)
    long_bg = np.zeros((window_height, total_width, 3), dtype=np.uint8)
    for i, bg in enumerate(backgrounds):
        long_bg[:, i * window_width:(i + 1) * window_width] = bg

    # 生成垃圾
    def random_garbage_pos(min_x, max_x, garbage_h, garbage_w):
        x = random.randint(min_x, max_x - garbage_w)
        y = random.randint(500, window_height - garbage_h - 10)
        return x, y

    garbage_items = []
    garbage_count = 50
    min_dist = 100

    # 生成垃圾
    for i in range(garbage_count):
        # 從垃圾矩陣中隨機選擇一種垃圾
        garbage_info = random.choice(garbage_matrix)
        garbage_file = garbage_info["file"]
        garbage_type = garbage_info["type"]
        
        # 獲取對應的垃圾圖像
        if garbage_file in garbage_images:
            garbage_image = garbage_images[garbage_file]
        else:
            # 如果找不到對應的圖像，使用第一個可用的圖像
            garbage_image = list(garbage_images.values())[0]
        
        garbage_h, garbage_w = garbage_image.shape[:2]
        
        while True:
            x, y = random_garbage_pos(0, total_width, garbage_h, garbage_w)
            # 檢查距離
            if all((x - item.x) ** 2 + (y - item.y) ** 2 >= min_dist ** 2 for item in garbage_items):
                break
        garbage_items.append(Garbage(garbage_image, x, y, garbage_type))
    
    # 載入指定的垃圾桶特寫背景
    recycle_custom_bg = cv2.imread('recycle_background/garbage_can_close.jpg')
    if recycle_custom_bg is not None:
        recycle_custom_bg = cv2.resize(recycle_custom_bg, (window_width, window_height))
    else:
        # 如果無法載入指定背景，則使用預設背景
        recycle_custom_bg = recycle_bg

    # 遊戲變數
    view_offset = 0
    max_view_offset = total_width - window_width
    character_x = window_width // 4
    character_y = 600
    collected_garbage = []
    score = 0
    step = 3
    font = cv2.FONT_HERSHEY_SIMPLEX

    # 拖拉垃圾相關變數
    is_dragging = False
    dragging_garbage_pos = [0, 0]  # 被拖拉的垃圾位置
    dragging_garbage_size = [0, 0]  # 被拖拉的垃圾大小

    # 垃圾桶位置和類型映射
    garbage_cans = [
        {"range": [300, 450, 420, 660], "type": "other", "bg": "other_open"},
        {"range": [500, 650, 420, 660], "type": "garbage", "bg": "garbage_open"},
        {"range": [700, 860, 420, 660], "type": "paper", "bg": "paper_open"},
        {"range": [915, 1075, 420, 660], "type": "iron", "bg": "iron_open"}
    ]

     # 角色動畫變數
    current_frame = 0
    frame_counter = 0
    is_moving = False
    facing_right = False  # 角色面向，False為左，True為右

    # 區域界限
    left_area_end = window_width // 2  # 背景1的左半邊結束點
    right_area_start = total_width - window_width // 2  # 背景5的右半邊開始點
    character_center_x = window_width // 2  # 角色在中間區域的固定位置
    # 切換畫面變數
    in_recycle_area = False
    
    
    mouse_x, mouse_y = 0, 0

    def mouse_callback(event, x, y, flags, param):
        nonlocal mouse_x, mouse_y, collected_garbage, score, is_dragging, dragging_garbage_pos
        mouse_x, mouse_y = x, y
        
        if in_recycle_area:
            if event == cv2.EVENT_LBUTTONDOWN:
                # 開始拖拉垃圾
                if collected_garbage and not is_dragging:
                    is_dragging = True
                    dragging_garbage_pos = [x, y]
            
            elif event == cv2.EVENT_MOUSEMOVE:
                # 更新拖拉位置
                if is_dragging:
                    dragging_garbage_pos = [x, y]
            
            elif event == cv2.EVENT_LBUTTONUP:
                # 放下垃圾，檢查是否在垃圾桶範圍內
                if is_dragging and collected_garbage:
                    is_dragging = False
                    
                    # 檢查是否在垃圾桶範圍內
                    garbage_type = collected_garbage[-1].garbage_type
                    for can in garbage_cans:
                        can_x_min, can_x_max, can_y_min, can_y_max = can["range"]
                        if can_x_min <= x <= can_x_max and can_y_min <= y <= can_y_max:
                            # 檢查類型是否匹配
                            if garbage_type == can["type"]:
                                score += 1
                                if ding_sound:
                                    ding_sound.play()
                            else:
                                score -= 1
                                if wrong_sound:
                                    wrong_sound.play()
                            
                            # 無論是否匹配，都移除垃圾
                            collected_garbage.pop()
                            return
                    
                    # 如果沒有放在垃圾桶區域，垃圾不會被移除
    
    cv2.setMouseCallback(window_name, mouse_callback)

    # 主遊戲迴圈
    while True:
        # 處理輸入
        if keyboard.is_pressed('q') or keyboard.is_pressed('esc'):
            break
        
        if in_recycle_area:
            # 已經在回收區域，直接設定角色為固定位置，不需要動畫
            is_moving = False  # 在回收區域，角色不移動
            if keyboard.is_pressed('down') or keyboard.is_pressed('s'):
                # 返回遊戲區域
                in_recycle_area = False
                view_offset = max_view_offset
                character_x = window_width - std_w - 50  # 設置角色在右側
                is_moving = True  # 離開時角色會移動
            # 以下移動控制被禁用
            # 角色固定在原位不動
        else:
            # 在遊戲區域時的處理
            # 計算角色在世界中的絕對位置
            world_pos = view_offset + character_x
            
            # 檢測是否有任何移動按鍵被按下
            is_moving = (
                keyboard.is_pressed('up') or keyboard.is_pressed('w') or
                keyboard.is_pressed('down') or keyboard.is_pressed('s') or
                keyboard.is_pressed('left') or keyboard.is_pressed('a') or
                keyboard.is_pressed('right') or keyboard.is_pressed('d')
            )
            
            # 上下移動 (始終允許)
            if keyboard.is_pressed('up') or keyboard.is_pressed('w'):
                character_y = max(430, character_y - step)
            if keyboard.is_pressed('down') or keyboard.is_pressed('s'):
                character_y = min(window_height - std_h, character_y + step)
            
            # 左右移動 (根據區域不同有不同行為)
            if keyboard.is_pressed('left') or keyboard.is_pressed('a'):
                facing_right = False  # 角色面向左邊
                if world_pos <= left_area_end:
                    # 在背景1的左半邊：自由移動角色
                    character_x = max(0, character_x - step)
                elif world_pos >= right_area_start:
                    # 在背景5的右半邊：自由移動角色
                    character_x = max(character_x - step, 0)
                else:
                    # 在中間區域：移動背景
                    view_offset = max(0, view_offset - step)
                    character_x = character_center_x  # 保持角色在中央
            
            if keyboard.is_pressed('right') or keyboard.is_pressed('d'):
                facing_right = True  # 角色面向右邊
                if world_pos < left_area_end:
                    # 在背景1的左半邊：自由移動角色
                    new_x = character_x + step
                    if view_offset == 0 and new_x + view_offset >= left_area_end:
                        # 即將進入中間區域
                        view_offset = new_x + view_offset - left_area_end
                        character_x = character_center_x
                    else:
                        character_x = min(window_width - std_w, new_x)
                elif world_pos >= right_area_start:
                    # 在背景5的右半邊：自由移動角色
                    if character_x + step >= window_width - std_w:
                        # 到達右邊界時直接切換到回收區域，不需要動畫
                        in_recycle_area = True
                    else:
                        character_x = min(character_x + step, window_width - std_w)
                else:
                    # 在中間區域：移動背景
                    if view_offset + step + character_center_x >= right_area_start:
                        # 即將進入右區域
                        character_x = right_area_start - view_offset
                        # 確保不超出右邊界
                        character_x = min(character_x, window_width - std_w)
                    else:
                        view_offset = min(max_view_offset, view_offset + step)
                        character_x = character_center_x  # 保持角色在中央
        
        # 更新角色動畫
        if is_moving:
            frame_counter += 1
            if frame_counter >= 3:  # 每5幀切換一次角色圖像
                frame_counter = 0
                current_frame = (current_frame + 1) % (len(std_frames_right) if facing_right else len(std_frames_left))
                # 根據角色面向選擇正確的動畫幀
                if facing_right:
                    std_rgb, alpha_mask = std_frames_right[current_frame]
                else:
                    std_rgb, alpha_mask = std_frames_left[current_frame]
        else:
            # 如果停止移動，顯示第一幀
            current_frame = 0
            # 根據角色面向選擇正確的靜止幀
            if facing_right:
                std_rgb, alpha_mask = std_frames_right[current_frame]
            else:
                std_rgb, alpha_mask = std_frames_left[current_frame]

        # 創建視圖
        view_frame = np.zeros((window_height, window_width, 3), dtype=np.uint8)

        if in_recycle_area:
        # 根據滑鼠位置決定使用哪個背景
            current_bg = 'default'  # 預設背景
            
            # 檢查滑鼠是否在垃圾桶範圍內
            for can in garbage_cans:
                can_x_min, can_x_max, can_y_min, can_y_max = can["range"]
                if can_x_min <= mouse_x <= can_x_max and can_y_min <= mouse_y <= can_y_max:
                    current_bg = can["bg"]
                    break
                    
            # 使用選定的背景
            view_frame[:] = recycle_backgrounds[current_bg]
            
            # 顯示頂端垃圾
            if collected_garbage:
                top_garbage = collected_garbage[-1]
                
                # 嘗試從X3garbage資料夾載入對應的圖片
                garbage_file = None
                
                # 找出目前垃圾的檔名
                for item in garbage_matrix:
                    if item["type"] == top_garbage.garbage_type:
                        garbage_file = item["file"]
                        break
                        
                if garbage_file:
                    # 直接從X3垃圾資料夾載入
                    x3_path = f'img/X3garbage/{garbage_file}'
                    if os.path.exists(x3_path):
                        garbage_img = cv2.imread(x3_path, cv2.IMREAD_UNCHANGED)
                        if garbage_img is None:  # 如果載入失敗，使用原始圖片並放大
                            garbage_img = top_garbage.image
                            garbage_img = cv2.resize(garbage_img, None, fx=3, fy=3, interpolation=cv2.INTER_NEAREST)
                    else:  # 如果X3版本不存在，使用原始圖片並放大
                        garbage_img = top_garbage.image
                        garbage_img = cv2.resize(garbage_img, None, fx=3, fy=3, interpolation=cv2.INTER_NEAREST)
                else:  # 如果找不到垃圾檔名，使用原始圖片並放大
                    garbage_img = top_garbage.image
                    garbage_img = cv2.resize(garbage_img, None, fx=3, fy=3, interpolation=cv2.INTER_NEAREST)
                
                garbage_h, garbage_w = garbage_img.shape[:2]
                # 如果正在拖拉，使用滑鼠位置；否則使用固定位置
                if is_dragging:
                    g_x, g_y = dragging_garbage_pos[0] - garbage_w // 2, dragging_garbage_pos[1] - garbage_h // 2
                else:
                    g_x, g_y = 1140, 30
                    dragging_garbage_pos = [g_x + garbage_w // 2, g_y + garbage_h // 2]
                
                # 確保垃圾在視窗範圍內
                g_x = max(0, min(g_x, window_width - garbage_w))
                g_y = max(0, min(g_y, window_height - garbage_h))
                
                # 繪製垃圾
                if garbage_img.shape[2] == 4:  # 有透明度通道
                    alpha = garbage_img[:, :, 3].astype(float) / 255.0
                    for c in range(3):
                        view_frame[g_y:g_y+garbage_h, g_x:g_x+garbage_w, c] = (
                            alpha * garbage_img[:, :, c] +
                            (1 - alpha) * view_frame[g_y:g_y+garbage_h, g_x:g_x+garbage_w, c]
                        )
                else:
                    view_frame[g_y:g_y+garbage_h, g_x:g_x+garbage_w] = garbage_img[:, :, :3]
                
                # 顯示當前垃圾類型
                cv2.putText(view_frame, f'Type: {top_garbage.garbage_type}', (10, 190), font, 1, (0, 0, 0), 2)
            
            # 顯示指示文字
            if collected_garbage:
                cv2.putText(view_frame, "Drag garbage to the correct bin", (window_width//2 - 200, 100), font, 1, (0, 0, 0), 2)
            else:
                cv2.putText(view_frame, "No garbage collected", (window_width//2 - 150, 100), font, 1, (0, 0, 0), 2)

        else:
            # 遊戲區域
            view_frame = long_bg[:, view_offset:view_offset + window_width].copy()
            
            # 繪製垃圾
            for item in garbage_items:
                if item.visible:
                    item_x = item.x - view_offset
                    item_image = item.image
                    item_h, item_w = item_image.shape[:2]
                    
                    if -item_w < item_x < window_width:
                        # 碰撞檢測
                        if (character_x < item_x + item_w and 
                            character_x + std_w > item_x and
                            character_y < item.y + item_h and 
                            character_y + std_h > item.y):
                            item.visible = False
                            collected_garbage.append(item)
                            continue
                        
                        # 繪製垃圾 - 處理部分顯示的情況
                        # 計算視窗內繪製的區域
                        x_start = max(0, item_x)
                        y_start = max(0, item.y)
                        x_end = min(item_x + item_w, window_width)
                        y_end = min(item.y + item_h, window_height)
                        
                        # 只有當有區域在視窗內才繪製
                        if x_end > x_start and y_end > y_start:
                            # 計算圖像上對應的起始點
                            img_start_x = 0 if item_x >= 0 else -item_x
                            img_start_y = 0 if item.y >= 0 else -item.y
                            
                            if item_image.shape[2] == 4:  # 有透明度
                                alpha = item_image[img_start_y:img_start_y+(y_end-y_start), 
                                                img_start_x:img_start_x+(x_end-x_start), 3].astype(float) / 255.0
                                for c in range(3):
                                    view_frame[y_start:y_end, x_start:x_end, c] = (
                                        alpha * item_image[img_start_y:img_start_y+(y_end-y_start), 
                                                          img_start_x:img_start_x+(x_end-x_start), c] +
                                        (1 - alpha) * view_frame[y_start:y_end, x_start:x_end, c]
                                    )
                            else:
                                view_frame[y_start:y_end, x_start:x_end] = item_image[img_start_y:img_start_y+(y_end-y_start), 
                                                                                    img_start_x:img_start_x+(x_end-x_start), :3]

        # 如果角色位置在視窗內且不是隱藏狀態，才繪製角色
        # 如果角色位置在視窗內且不是隱藏狀態，且不在回收區域時才繪製角色
        if 0 <= character_x < window_width and 0 <= character_y < window_height and not in_recycle_area:
            char_y_end = min(character_y + std_h, window_height)
            char_x_end = min(character_x + std_w, window_width)
            
            for c in range(3):
                view_frame[character_y:char_y_end, character_x:char_x_end, c] = (
                    alpha_mask[:char_y_end-character_y, :char_x_end-character_x] * 
                    std_rgb[:char_y_end-character_y, :char_x_end-character_x, c] +
                    (1 - alpha_mask[:char_y_end-character_y, :char_x_end-character_x]) * 
                    view_frame[character_y:char_y_end, character_x:char_x_end, c]
                )

        # 顯示分數和收集數量
        cv2.putText(view_frame, f'Score: {score}', (10, 30), font, 1, (0, 0, 0), 2)
        cv2.putText(view_frame, f'Collected: {len(collected_garbage)}', (10, 70), font, 1, (0, 0, 0), 2)
        
        # 顯示最近收集的垃圾類型
        if collected_garbage:
            last_garbage = collected_garbage[-1]
            cv2.putText(view_frame, f'Last: {last_garbage.garbage_type}', (10, 150), font, 1, (0, 0, 0), 2)
        
        # 顯示目前區域
        area_text = ""
        if in_recycle_area:
            area_text = "Recycle Area"
        elif world_pos < left_area_end:
            area_text = "Left Area"
        elif world_pos >= right_area_start:
            area_text = "Right Area"
        else:
            area_text = "Middle Area"
        cv2.putText(view_frame, area_text, (10, 110), font, 1, (0, 0, 0), 2)

        cv2.imshow(window_name, view_frame)
        cv2.waitKey(5)

def main():
    window_name = 'Beach Game'
    from menu import show_menu
    show_menu(window_name)
    beach_game(window_name)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()