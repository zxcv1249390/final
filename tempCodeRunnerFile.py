# 載入角色動畫圖像 - 向右走
    std_frames_right = []
    for i in range(1, 13):  # 載入1.png到12.png
        frame = cv2.imread(f'img/std_moving_right/{i}.png', cv2.IMREAD_UNCHANGED)
        if frame is not None:
            frame_rgb = frame[..., :3]
            frame_alpha = frame[..., 3].astype(float) / 255.0
            std_frames_right.append((frame_rgb, frame_alpha))