import cv2
from menu import show_menu, show_guide
from game import beach_game

# 主程式
def main():
    window_name = 'Beach Game'
    show_menu(window_name)
    show_guide(window_name)
    beach_game(window_name)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()