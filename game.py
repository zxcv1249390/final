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
    for i in range(1, 13):  # 載入1.png到12.png
        frame_path = f'img/std_moving_right/{i}.png'
        frame = cv2.imread(frame_path, cv2.IMREAD_UNCHANGED)
        if frame is not None:
            frame_rgb = frame[..., :3]
            frame_alpha = frame[..., 3].astype(float) / 255.0
            std_frames_right.append((frame_rgb, frame_alpha))

    # 載入角色動畫圖像 - 向左走
    std_frames_left = []
    for i in range(1, 13):  # 載入1.png到12.png
        frame = cv2.imread(f'img/std_moving_left/{i}.png', cv2.IMREAD_UNCHANGED)
        if frame is not None:
            frame_rgb = frame[..., :3]
            frame_alpha = frame[..., 3].astype(float) / 255.0
            std_frames_left.append((frame_rgb, frame_alpha))
    
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

    # 載入垃圾圖像 (這只是預設，實際會從 matrix 載入)
    garbage = cv2.imread('img/garbage/cola.png', cv2.IMREAD_UNCHANGED)
    if garbage is not None:
        garbage = cv2.resize(garbage, None, fx=0.5, fy=0.5)
    else:
        garbage = np.full((30, 20, 4), (0, 255, 0, 255), dtype=np.uint8)

    # 載入最終畫面圖片
    final_image = cv2.imread('img/final.png')
    if final_image is not None:
        final_image = cv2.resize(final_image, (window_width, window_height))
    else:
        final_image = np.full((window_height, window_width, 3), (255, 255, 255), dtype=np.uint8) # 白色預設背景

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
        'wrong_sound': wrong_sound,
        'final_image': final_image 
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
    std_frames_left = assets['std_frames_left']  # 向左走的動畫幀
    std_frames_right = assets['std_frames_right']  # 向右走的動畫幀
    ding_sound = assets['ding_sound']
    wrong_sound = assets['wrong_sound']
    final_image = assets['final_image'] 
    
    # 預先載入所有回收區背景圖片
    recycle_backgrounds = {
        'default': cv2.imread('recycle_background/garbage_can_close.jpg'),
        'other_open': cv2.imread('recycle_background/other_open.jpg'),
        'garbage_open': cv2.imread('recycle_background/garbage_open.jpg'),
        'paper_open': cv2.imread('recycle_background/paper_open.jpg'),
        'iron_open': cv2.imread('recycle_background/iron_open.jpg'),
    }
    # 確保所有背景圖片都正確載入並調整大小
    for key, img in recycle_backgrounds.items():
        if img is not None:
            recycle_backgrounds[key] = cv2.resize(img, (window_width, window_height))
        else:
            print(f"警告: {key} 背景圖片載入失敗，使用預設關閉垃圾桶背景替代。")
            if 'default' in recycle_backgrounds and recycle_backgrounds['default'] is not None:
                 recycle_backgrounds[key] = recycle_backgrounds['default'].copy()
            else: 
                 recycle_backgrounds[key] = np.full((window_height, window_width, 3), (0, 0, 0), dtype=np.uint8)


    # 載入指定的垃圾桶特寫背景
    recycle_custom_bg = cv2.imread('recycle_background/garbage_can_close.jpg')
    if recycle_custom_bg is not None:
        recycle_custom_bg = cv2.resize(recycle_custom_bg, (window_width, window_height))
    else:
        recycle_custom_bg = recycle_bg

    # 角色尺寸
    std_h, std_w = std_frames_left[0][0].shape[:2] 

    # 定義垃圾矩陣
    garbage_matrix = [
        {"file": "bottle_01.png", "type": "other"},
        {"file": "box.png", "type": "paper"},
        {"file": "chips.png", "type": "garbage"},
        {"file": "cola.png", "type": "other"},
        {"file": "garbage_bag_01.png", "type": "garbage"},
        {"file": "Mai_box.png", "type": "paper"},
        {"file": "milk_box.png", "type": "paper"},
        {"file": "pepsi_can.png", "type": "iron"},
        {"file": "straw_01.png", "type": "garbage"},
        {"file": "tissue_01.png", "type": "garbage"},
        {"file": "shell_01.png", "type": "shell"}, 
        {"file": "shell_02.png", "type": "shell"}  
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
    
    # 遊戲變數
    view_offset = 0
    max_view_offset = total_width - window_width
    character_x = window_width // 4
    character_y = 600
    collected_garbage = []
    score = 0
    step = 10
    font = cv2.FONT_HERSHEY_SIMPLEX

    # 拖拉垃圾相關變數
    is_dragging = False
    dragging_garbage_pos = [0, 0]  # 被拖拉的垃圾位置

    # 垃圾桶位置和類型映射
    garbage_cans = [
        {"range": [300, 450, 420, 660], "type": "other", "bg": "other_open", "score_multiplier": 1},
        {"range": [500, 650, 420, 660], "type": "garbage", "bg": "garbage_open", "score_multiplier": 1},
        {"range": [700, 860, 420, 660], "type": "paper", "bg": "paper_open", "score_multiplier": 1},
        {"range": [915, 1075, 420, 660], "type": "iron", "bg": "iron_open", "score_multiplier": 1},
        {"range": [1180, 1280, 420, 660], "type": "shell", "bg": "garbage_can_close", "score_multiplier": 2} 
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
    game_over = False # 新增遊戲結束狀態
    
    mouse_x, mouse_y = 0, 0

    def mouse_callback(event, x, y, flags, param):
        nonlocal mouse_x, mouse_y, collected_garbage, score, is_dragging, dragging_garbage_pos, game_over
        mouse_x, mouse_y = x, y
        
        if in_recycle_area:
            if event == cv2.EVENT_LBUTTONDOWN:
                # 開始拖拉垃圾
                if collected_garbage and not is_dragging:
                    is_dragging = True
                    if collected_garbage:
                        dragging_garbage_pos = [x, y]
            
            elif event == cv2.EVENT_MOUSEMOVE:
                # 更新拖拉位置
                if is_dragging:
                    dragging_garbage_pos = [x, y]
            
            elif event == cv2.EVENT_LBUTTONUP:
                # 放下垃圾，檢查是否在垃圾桶範圍內
                if is_dragging and collected_garbage: 
                    is_dragging = False
                    
                    garbage_type = collected_garbage[-1].garbage_type
                    dropped_correctly = False 
                    for can in garbage_cans:
                        can_x_min, can_x_max, can_y_min, can_y_max = can["range"]
                        if can_x_min <= x <= can_x_max and can_y_min <= y <= can_y_max:
                            # 檢查類型是否匹配
                            if garbage_type == can["type"]:
                                score_to_add = 1 * can.get("score_multiplier", 1) 
                                score += score_to_add
                                if ding_sound:
                                    ding_sound.play()
                                dropped_correctly = True 
                            else:
                                score -= 1
                                if wrong_sound:
                                    wrong_sound.play()
                                dropped_correctly = True 
                            
                            # 無論是否匹配，都移除垃圾
                            collected_garbage.pop()
                            break 

                    # 如果沙灘上沒有垃圾，且 collected_garbage 也清空了，則遊戲結束
                    if len([item for item in garbage_items if item.visible]) == 0 and not collected_garbage:
                         game_over = True
                
    cv2.setMouseCallback(window_name, mouse_callback)

    # 主遊戲迴圈
    while True:
        # 處理輸入
        if keyboard.is_pressed('q') or keyboard.is_pressed('esc'):
            break
        
        if game_over:
            # 遊戲結束畫面
            display_frame = final_image.copy()
            score_text = f"Final Score: {score}"
            text_size = cv2.getTextSize(score_text, font, 2, 3)[0] 
            text_x = (window_width - text_size[0]) // 2
            text_y = (window_height + text_size[1]) // 2
            cv2.putText(display_frame, score_text, (text_x, text_y), font, 2, (0, 0, 255), 3) 
            cv2.imshow(window_name, display_frame)
            cv2.waitKey(5) 

            if keyboard.is_pressed('q'): 
                break
            continue 
            
        if in_recycle_area:
            is_moving = False 
            # 角色不顯示，所以不再需要 character_x_display 和 character_y_display
            # 但我們仍需要檢查返回遊戲區域的指令
            if keyboard.is_pressed('down') or keyboard.is_pressed('s'):
                in_recycle_area = False
                view_offset = max_view_offset
                character_x = window_width - std_w - 50 
                is_moving = True 
        else:
            world_pos = view_offset + character_x
            
            is_moving = (
                keyboard.is_pressed('up') or keyboard.is_pressed('w') or
                keyboard.is_pressed('down') or keyboard.is_pressed('s') or
                keyboard.is_pressed('left') or keyboard.is_pressed('a') or
                keyboard.is_pressed('right') or keyboard.is_pressed('d')
            )
            
            if keyboard.is_pressed('up') or keyboard.is_pressed('w'):
                character_y = max(430, character_y - step)
            if keyboard.is_pressed('down') or keyboard.is_pressed('s'):
                character_y = min(window_height - std_h, character_y + step)
            
            if keyboard.is_pressed('left') or keyboard.is_pressed('a'):
                facing_right = False 
                if world_pos <= left_area_end:
                    character_x = max(0, character_x - step)
                elif world_pos >= right_area_start:
                    character_x = max(character_x - step, 0)
                else:
                    view_offset = max(0, view_offset - step)
                    character_x = character_center_x 
            
            if keyboard.is_pressed('right') or keyboard.is_pressed('d'):
                facing_right = True 
                if world_pos < left_area_end:
                    new_x = character_x + step
                    if view_offset == 0 and new_x + view_offset >= left_area_end:
                        view_offset = new_x + view_offset - left_area_end
                        character_x = character_center_x
                    else:
                        character_x = min(window_width - std_w, new_x)
                elif world_pos >= right_area_start:
                    if character_x + step >= window_width - std_w:
                        in_recycle_area = True
                        # 進入回收區時，不再設定角色顯示位置，因為它會隱藏
                    else:
                        character_x = min(character_x + step, window_width - std_w)
                else:
                    if view_offset + step + character_center_x >= right_area_start:
                        character_x = right_area_start - view_offset
                        character_x = min(character_x, window_width - std_w)
                    else:
                        view_offset = min(max_view_offset, view_offset + step)
                        character_x = character_center_x 

        # 更新角色動畫
        # 只有在不在回收區時才更新動畫
        if not in_recycle_area:
            if is_moving:
                frame_counter += 1
                if frame_counter >= 3: 
                    frame_counter = 0
                    current_frame = (current_frame + 1) % (len(std_frames_right) if facing_right else len(std_frames_left))
                    if facing_right:
                        std_rgb, alpha_mask = std_frames_right[current_frame]
                    else:
                        std_rgb, alpha_mask = std_frames_left[current_frame]
            else:
                current_frame = 0
                if facing_right:
                    std_rgb, alpha_mask = std_frames_right[current_frame]
                else:
                    std_rgb, alpha_mask = std_frames_left[current_frame]

        # 創建視圖
        view_frame = np.zeros((window_height, window_width, 3), dtype=np.uint8)

        if in_recycle_area:
            current_bg = 'default' 
            for can in garbage_cans:
                can_x_min, can_x_max, can_y_min, can_y_max = can["range"]
                if can_x_min <= mouse_x <= can_x_max and can_y_min <= mouse_y <= can_y_max:
                    current_bg = can["bg"]
                    break
                    
            if current_bg in recycle_backgrounds and recycle_backgrounds[current_bg] is not None and recycle_backgrounds[current_bg].shape[:2] == (window_height, window_width):
                view_frame[:] = recycle_backgrounds[current_bg]
            else:
                view_frame[:] = recycle_custom_bg 
            
            # 顯示頂端垃圾
            if collected_garbage:
                top_garbage = collected_garbage[-1]
                
                matched_garbage_info = None
                for item_info in garbage_matrix:
                    if item_info["type"] == top_garbage.garbage_type:
                        matched_garbage_info = item_info
                        break
                
                garbage_img = None
                if matched_garbage_info:
                    garbage_file = matched_garbage_info["file"]
                    x3_path = f'img/X3garbage/{garbage_file}'
                    if os.path.exists(x3_path):
                        garbage_img = cv2.imread(x3_path, cv2.IMREAD_UNCHANGED)
                        if garbage_img is None:  
                            garbage_img = top_garbage.image
                            garbage_img = cv2.resize(garbage_img, None, fx=3, fy=3, interpolation=cv2.INTER_NEAREST)
                    else:  
                        garbage_img = top_garbage.image
                        garbage_img = cv2.resize(garbage_img, None, fx=3, fy=3, interpolation=cv2.INTER_NEAREST)
                else: 
                    garbage_img = top_garbage.image
                    garbage_img = cv2.resize(garbage_img, None, fx=3, fy=3, interpolation=cv2.INTER_NEAREST)
                
                if garbage_img is not None: 
                    garbage_h, garbage_w = garbage_img.shape[:2]
                    if is_dragging:
                        g_x, g_y = dragging_garbage_pos[0] - garbage_w // 2, dragging_garbage_pos[1] - garbage_h // 2
                    else:
                        g_x, g_y = 1140, 30
                        dragging_garbage_pos = [g_x + garbage_w // 2, g_y + garbage_h // 2]
                    
                    g_x = max(0, min(g_x, window_width - garbage_w))
                    g_y = max(0, min(g_y, window_height - garbage_h))
                    
                    if garbage_img.shape[2] == 4:  
                        alpha = garbage_img[:, :, 3].astype(float) / 255.0
                        for c in range(3):
                            view_frame[g_y:g_y+garbage_h, g_x:g_x+garbage_w, c] = (
                                alpha * garbage_img[:, :, c] +
                                (1 - alpha) * view_frame[g_y:g_y+garbage_h, g_x:g_x+garbage_w, c]
                            )
                    else:
                        view_frame[g_y:g_y+garbage_h, g_x:g_x+garbage_w] = garbage_img[:, :, :3]
                    
                    cv2.putText(view_frame, f'Type: {top_garbage.garbage_type}', (10, 190), font, 1, (0, 0, 0), 2)
            
            if collected_garbage:
                cv2.putText(view_frame, "Drag garbage to the correct bin", (window_width//2 - 200, 100), font, 1, (0, 0, 0), 2)
            else:
                cv2.putText(view_frame, "No garbage collected", (window_width//2 - 150, 100), font, 1, (0, 0, 0), 2)

        else: # 遊戲區域
            view_frame = long_bg[:, view_offset:view_offset + window_width].copy()
            
            for item in garbage_items:
                if item.visible:
                    item_x = item.x - view_offset
                    item_image = item.image
                    item_h, item_w = item_image.shape[:2]
                    
                    if -item_w < item_x < window_width:
                        character_lower_quarter_y = character_y + int(std_h * 3 / 4)
                        character_lower_quarter_h = std_h - int(std_h * 3 / 4)

                        if (character_x < item_x + item_w and
                                character_x + std_w > item_x and
                                character_lower_quarter_y < item.y + item_h and
                                character_lower_quarter_y + character_lower_quarter_h > item.y):
                            item.visible = False
                            collected_garbage.append(item)
                            continue
                        
                        x_start = max(0, item_x)
                        y_start = max(0, item.y)
                        x_end = min(item_x + item_w, window_width)
                        y_end = min(item.y + item_h, window_height)
                        
                        if x_end > x_start and y_end > y_start:
                            img_start_x = 0 if item_x >= 0 else -item_x
                            img_start_y = 0 if item.y >= 0 else -item.y
                            
                            if item_image.shape[2] == 4:  
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

            if len([item for item in garbage_items if item.visible]) == 0 and not collected_garbage and not in_recycle_area:
                game_over = True 
        
        # 繪製角色 - 只有當不在回收區域時才繪製角色
        if not in_recycle_area:
            # 在遊戲區域時，角色實際位置就是character_x和character_y
            char_y_end = min(character_y + std_h, window_height)
            char_x_end = min(character_x + std_w, window_width)
            
            # 確保擷取正確大小的圖片區域
            current_std_rgb = std_rgb[:char_y_end-character_y, :char_x_end-character_x, :]
            current_alpha_mask = alpha_mask[:char_y_end-character_y, :char_x_end-character_x]

            if current_std_rgb.shape[0] > 0 and current_std_rgb.shape[1] > 0:
                for c in range(3):
                    view_frame[character_y:char_y_end, character_x:char_x_end, c] = (
                        current_alpha_mask * current_std_rgb[:, :, c] +
                        (1 - current_alpha_mask) * view_frame[character_y:char_y_end, character_x:char_x_end, c]
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
    if not os.path.exists('final.png'):
        print("警告: final.png 不存在。請在程式相同目錄下放置 final.png 圖片，或者程式將會使用白色背景代替。")
        temp_final_img = np.full((810, 1350, 3), (200, 200, 200), dtype=np.uint8) 
        cv2.putText(temp_final_img, "Final Screen Placeholder", (400, 400), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        
    from menu import show_menu 
    show_menu(window_name)
    beach_game(window_name)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
#程式結束!!