#game.py

import cv2
import numpy as np
import random
import keyboard
import pygame
from assets import load_images
import os

def beach_game(window_name):
    window_width = 1500
    window_height = 900
    assets = load_images(window_width, window_height)
    backgrounds = assets['backgrounds']
    recycle_bg = assets['recycle_bg']
    garbage_cans = assets['garbage_cans']
    std_rgb = assets['std_rgb']
    alpha_mask = assets['alpha_mask']
    garbage_rgb = assets['garbage_rgb']
    garbage_alpha = assets['garbage_alpha']
    ding_sound = assets['ding_sound']
    wrong_sound = assets['wrong_sound']

    std_h, std_w = std_rgb.shape[:2]
    garbage_h, garbage_w = garbage_rgb.shape[:2]

    garbage_can_positions = []
    if garbage_cans:
        gc_height = garbage_cans[0].shape[0]
        gc_width = garbage_cans[0].shape[1]
        spacing = window_width // (len(garbage_cans) + 1)
        for i in range(len(garbage_cans)):
            x = spacing * (i + 1) - gc_width // 2
            y = window_height // 2 - gc_height // 2
            garbage_can_positions.append((x, y))

    total_width = window_width * len(backgrounds)
    long_bg = np.zeros((window_height, total_width, 3), dtype=np.uint8)
    for i, bg in enumerate(backgrounds):
        long_bg[:, i * window_width:(i + 1) * window_width] = bg

    if std_h > window_height // 3:
        scale = (window_height // 3) / std_h
        new_w = int(std_w * scale)
        new_h = int(std_h * scale)
        std_rgb = cv2.resize(std_rgb, (new_w, new_h), interpolation=cv2.INTER_AREA)
        alpha_mask = cv2.resize(alpha_mask, (new_w, new_h), interpolation=cv2.INTER_AREA)
        std_h, std_w = new_h, new_w

    def random_garbage_pos(min_x, max_x):
        world_x = random.randint(min_x, max_x - garbage_w)
        y = random.randint(600, window_height - garbage_h - 10)
        return world_x, y

    class Garbage:
        def __init__(self, image, x, y, category):
            self.image = image
            self.x = x
            self.y = y
            self.visible = True
            self.category = category

    garbage_images = []
    garbage_dir = 'img/garbage'
    for filename in os.listdir(garbage_dir):
        if filename.endswith('.png'):
            img_path = os.path.join(garbage_dir, filename)
            image = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
            if 'cola' in filename or 'bottle' in filename:
                category = 'plastic'
            elif 'paper' in filename or 'box' in filename:
                category = 'paper'
            elif 'can' in filename:
                category = 'metal'
            else:
                category = 'other'
            garbage_images.append((image, category))

    garbage_items = []
    min_dist = 150
    min_dist_sq = min_dist * min_dist
    garbage_count = 35
    garbage_per_bg = garbage_count // len(backgrounds)

    for bg_idx in range(len(backgrounds)):
        bg_start_x = bg_idx * window_width
        bg_end_x = (bg_idx + 1) * window_width
        for i in range(garbage_per_bg):
            while True:
                x, y = random_garbage_pos(bg_start_x, bg_end_x)
                if all((x - item.x) ** 2 + (y - item.y) ** 2 >= min_dist_sq for item in garbage_items):
                    break
            image, category = random.choice(garbage_images)
            garbage_items.append(Garbage(image, x, y, category))

    remaining = garbage_count - (garbage_per_bg * len(backgrounds))
    for i in range(remaining):
        while True:
            x, y = random_garbage_pos(0, total_width)
            if all((x - item.x) ** 2 + (y - item.y) ** 2 >= min_dist_sq for item in garbage_items):
                break
        image, category = random.choice(garbage_images)
        garbage_items.append(Garbage(image, x, y, category))

    free_move_start = 0
    fixed_char_start = window_width // 2
    fixed_char_end = total_width - window_width // 2
    free_move_end = total_width

    view_offset = 0
    max_view_offset = total_width - window_width

    character_x = window_width // 4
    character_y = 600

    in_recycle_area = False
    collected_garbage = []

    mouse_x, mouse_y = 0, 0
    hovered_can_index = -1
    classification_message = ''
    message_counter = 0

    def mouse_callback(event, x, y, flags, param):
        nonlocal mouse_x, mouse_y, hovered_can_index, collected_garbage, score, classification_message, message_counter
        mouse_x, mouse_y = x, y

        if in_recycle_area and event == cv2.EVENT_LBUTTONDOWN:
            if hovered_can_index != -1 and collected_garbage:
                can_category = ['plastic', 'paper', 'metal', 'other'][hovered_can_index]
                current_item = collected_garbage.pop()
                if current_item.category == can_category:
                    score += 1
                    ding_sound.play()
                    classification_message = 'Correct! +1'
                else:
                    score = max(0, score - 1)
                    wrong_sound.play()
                    classification_message = 'Wrong! -1'
                message_counter = 60

    cv2.setMouseCallback(window_name, mouse_callback)

    step = 5
    score = 0
    font = cv2.FONT_HERSHEY_SIMPLEX

    while True:
        if view_offset >= max_view_offset and character_x >= window_width - std_w - 10:
            in_recycle_area = True
        elif view_offset < max_view_offset - 100:
            in_recycle_area = False

        view_frame = np.zeros((window_height, window_width, 3), dtype=np.uint8)

        if in_recycle_area:
            view_frame[:] = recycle_bg
            hovered_can_index = -1
            category_names = ['Plastic', 'Paper', 'Metal', 'Other']

            for i, (x, y) in enumerate(garbage_can_positions):
                gc = garbage_cans[i]
                gc_alpha = gc[..., 3].astype(float) / 255.0
                scale_factor = 1.2 if x <= mouse_x < x + gc.shape[1] and y <= mouse_y < y + gc.shape[0] else 1.0
                if scale_factor > 1.0:
                    original_height, original_width = gc.shape[:2]
                    new_width = int(original_width * scale_factor)
                    new_height = int(original_height * scale_factor)
                    resized_gc = cv2.resize(gc, (new_width, new_height), interpolation=cv2.INTER_AREA)
                    x_offset = (new_width - original_width) // 2
                    y_offset = (new_height - original_height) // 2
                    x = x - x_offset
                    y = y - y_offset
                    gc = resized_gc
                    gc_alpha = gc[..., 3].astype(float) / 255.0
                    hovered_can_index = i

                gc_h, gc_w = gc.shape[:2]
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

                # Draw category name
                text = category_names[i]
                text_size, _ = cv2.getTextSize(text, font, 1, 2)
                text_x = x + (gc_w - text_size[0]) // 2
                text_y = y - 10
                cv2.putText(view_frame, text, (text_x, text_y), font, 1, (255, 255, 255), 2, cv2.LINE_AA)

            if collected_garbage:
                preview = collected_garbage[0].image
                preview_rgb = preview[..., :3]
                preview_alpha = preview[..., 3] / 255.0
                ph, pw = preview.shape[:2]
                x0, y0 = window_width - pw - 30, 30
                for c in range(3):
                    view_frame[y0:y0+ph, x0:x0+pw, c] = (
                        preview_alpha * preview_rgb[:, :, c] +
                        (1 - preview_alpha) * view_frame[y0:y0+ph, x0:x0+pw, c]
                    ).astype(np.uint8)

        else:
            view_offset = max(0, min(view_offset, max_view_offset))
            view_frame[:] = long_bg[:, view_offset:view_offset + window_width]
            character_world_x = view_offset + character_x

            if character_world_x < fixed_char_start:
                character_screen_x = character_x
                view_offset = 0
            elif character_world_x >= fixed_char_end:
                view_offset = max_view_offset
                character_screen_x = character_world_x - view_offset
            else:
                character_screen_x = window_width // 2
                view_offset = character_world_x - character_screen_x

            for garbage_item in garbage_items:
                if garbage_item.visible:
                    garbage_image = garbage_item.image
                    garbage_alpha = garbage_image[:, :, 3] / 255.0
                    garbage_rgb = garbage_image[:, :, :3]
                    garbage_screen_x = garbage_item.x - view_offset
                    garbage_y = garbage_item.y

                    if -garbage_image.shape[1] < garbage_screen_x < window_width:
                        visible_x_start = max(0, garbage_screen_x)
                        garbage_x_offset = visible_x_start - garbage_screen_x
                        visible_x_end = min(window_width, garbage_screen_x + garbage_image.shape[1])
                        visible_width = visible_x_end - visible_x_start
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

            character_y_end = min(window_height, character_y + std_h)
            character_height = character_y_end - character_y
            character_screen_x = max(0, min(window_width - std_w, character_screen_x))

            if character_height > 0:
                for c in range(3):
                    view_frame[character_y:character_y_end, character_screen_x:character_screen_x + std_w, c] = (
                        alpha_mask[:character_height, :] * std_rgb[:character_height, :, c] +
                        (1 - alpha_mask[:character_height, :]) * view_frame[character_y:character_y_end,
                                                                     character_screen_x:character_screen_x + std_w, c]
                    ).astype(np.uint8)

        # 顯示分數
        cv2.putText(view_frame, f"Score: {score}", (40, 120), font, 2, (0, 0, 255), 4, cv2.LINE_AA)

        # 顯示分類結果提示
        if message_counter > 0:
            color = (0, 255, 0) if 'Correct' in classification_message else (0, 0, 255)
            cv2.putText(view_frame, classification_message, (40, 180), font, 2, color, 4, cv2.LINE_AA)
            message_counter -= 1

        cv2.imshow(window_name, view_frame)

        key = cv2.waitKey(10)
        if keyboard.is_pressed('q') or key == 27:
            break

        up = keyboard.is_pressed('w') or keyboard.is_pressed('up')
        down = keyboard.is_pressed('s') or keyboard.is_pressed('down')
        left = keyboard.is_pressed('a') or keyboard.is_pressed('left')
        right = keyboard.is_pressed('d') or keyboard.is_pressed('right')

        character_y = max(430, min(window_height - std_h, character_y + (down - up) * step))

        if not in_recycle_area:
            if left:
                character_world_x = max(0, character_world_x - step)
            if right:
                character_world_x = min(total_width - std_w, character_world_x + step)

            if character_world_x < fixed_char_start:
                character_x = character_world_x
                view_offset = 0
            elif character_world_x >= fixed_char_end:
                view_offset = max_view_offset
                character_x = character_world_x - view_offset
            else:
                character_x = window_width // 2
                view_offset = character_world_x - character_x
        else:
            if left and not collected_garbage:
                in_recycle_area = False
                view_offset = max_view_offset - 100

        if not in_recycle_area and not collected_garbage:
            for idx, garbage_item in enumerate(garbage_items):
                if garbage_item.visible:
                    garbage_screen_x = garbage_item.x - view_offset
                    garbage_y = garbage_item.y
                    if -garbage_w < garbage_screen_x < window_width:
                        if (abs(character_screen_x + std_w / 2 - (garbage_screen_x + garbage_w / 2)) < (std_w + garbage_w) / 2 and
                            abs(character_y + std_h / 2 - (garbage_y + garbage_h / 2)) < (std_h + garbage_h) / 2):
                            collected_garbage.append(garbage_item)
                            garbage_item.visible = False
                            ding_sound.play()
                            break
