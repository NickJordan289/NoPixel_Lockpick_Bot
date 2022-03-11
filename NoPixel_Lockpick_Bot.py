import numpy as np # Math
import cv2 # Computer vision 
import pyautogui # Button pressing
import mss # Screen grabbing
import ctypes # Windows Get Resolution

# State Values
RESET = 0
FOUND = 1
INTERCEPTION = 2

# Default values
state = RESET
starting_area = 0
number = 0
screen_width = ctypes.windll.user32.GetSystemMetrics(0)
prev_area = 0

# Set test to true if testing on 
# https://sharkiller.ddns.net/nopixel_minigame/lockpicks/
test = True
if test: 
    template_path_prefix = 'templates/web/'
    # Set crop zones
    zone = {"top": 175, "left": int(0.46*screen_width), "width": 184, "height": 161} # Zone around bar
    number_zone = {"top": 30, "left": 55, "width": 65, "height": 100} # Zone around number
    # Set colour ranges for bar
    blue_bar_lower = np.array([80, 70, 105], dtype="uint8") # Min HSV threshold for blue target bar
    blue_bar_upper = np.array([98, 255, 200], dtype="uint8") # Max HSV threshold for blue target bar
else: 
    template_path_prefix = 'templates/'
    # Set crop zones
    zone = {"top": 815, "left": 1190, "width": 180, "height": 180} # Zone around bar
    number_zone = {"top": 60, "left": 70, "width": 40, "height": 50} # Zone around number
    # Set colour ranges for bar
    blue_bar_lower = np.array([85, 187, 50], dtype="uint8") # Min HSV threshold for blue target bar
    blue_bar_upper = np.array([93, 255, 178], dtype="uint8") # Max HSV threshold for blue target bar

# Preload templates
templates = []
for i,template_path in enumerate(['1.png', '2.png', '3.png', '4.png']):
        templates.append(cv2.imread(f'{template_path_prefix}{template_path}', 0))

# Main loop
while True:    
    # Get screenshot
    with mss.mss() as sct:
        frame = cv2.cvtColor(np.array(sct.grab(zone)), cv2.COLOR_BGR2HSV)

    # Get area of target bar
    mask = cv2.inRange(frame, blue_bar_lower, blue_bar_upper)
    area = np.sum(mask == 255)

    # Update State
    if state == FOUND and area/starting_area <= 0.9:
        state = INTERCEPTION
    elif state == RESET and area > 0:
        state = FOUND
        starting_area = area
    elif area == 0 and (state == FOUND or state == INTERCEPTION):
        state = RESET
        starting_area = 0

    # Find Number to press
    if number == 0 or area != prev_area:
        number_crop = frame[number_zone["top"]:number_zone["top"]+number_zone["height"],number_zone["left"]:number_zone["left"]+number_zone["width"]]
        number_crop = cv2.cvtColor(number_crop, cv2.COLOR_HSV2BGR)
        img_gray = cv2.cvtColor(number_crop, cv2.COLOR_BGR2GRAY)
        for i,template in enumerate(templates):
            res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
            threshold = 0.8
            loc = np.where(res >= threshold)
            found = len(loc[0])
            if found > 0:
                number = i+1
        prev_area = area

    # Press number when in right zone
    if state == INTERCEPTION and number != 0:
        pyautogui.press(f'{number}')
        state = RESET
        number = 0    