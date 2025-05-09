import tkinter as tk
from math import sin, cos, radians
from pynput import mouse
import time
import numpy as np

# --- Full circumplex emotions with approximate angle mapping
detected_release = False
emotion_angle_map = {
    "excited": 30, "alert": 60, "nervous": 90, "stressed": 120,
    "tired": 150, "bored": 180, "depressed": 210, "calm": 240,
    "relaxed": 270, "serene": 300, "content": 330
}

angle_emotion_map = {v: k for k, v in emotion_angle_map.items()}
angle_list = sorted(angle_emotion_map.keys())

# --- New crisp certainty logic
def get_certainty_label(hold_time):
    if hold_time >= 15:
        return "very sure", 1.0
    elif hold_time >= 7:
        return "sure", 0.66
    else:
        return "uncertain", 0.33

# --- Get nearest emotion to current angle
def emotion_from_angle(angle):
    closest_angle = min(angle_list, key=lambda x: abs(x - angle))
    return angle_emotion_map[closest_angle], closest_angle

# --- Movement tracker
last_move_time = time.time()
current_pos = (0, 0)
needle_angle = 30  # initial needle position
selected_emotion = None
holding_start_time = None
measuring_certainty = False
certainty_result = None
holding_mouse = False
mouse_moving = False
locked_angle = None

# --- Mouse listener
def on_move(x, y):
    global last_move_time, current_pos, needle_angle, mouse_moving, locked_angle
    if holding_mouse and locked_angle is not None:
        return
        
    if (x, y) != current_pos:
        last_move_time = time.time()
        current_pos = (x, y)
        mouse_moving = True
        dx = x % 300
        needle_angle = int((dx / 300) * 360) % 360

def on_click(x, y, button, pressed):
    global holding_start_time, holding_mouse, mouse_moving, locked_angle, certainty_result
    if pressed:
        holding_start_time = time.time()
        holding_mouse = True
        mouse_moving = True
        locked_angle = None
        certainty_result = None
    else:
        holding_mouse = False
        mouse_moving = False
        if holding_start_time and locked_angle is not None:
            hold_time = time.time() - holding_start_time
            certainty_label, certainty_score = get_certainty_label(hold_time)
            certainty_result = (certainty_label, certainty_score)
            print(f"Selected: {selected_emotion} ({certainty_label})")
        locked_angle = None

# --- Check for movement stop
def check_movement():
    global mouse_moving, locked_angle, holding_start_time
    if holding_mouse and not mouse_moving and locked_angle is None:
        locked_angle = needle_angle
        holding_start_time = time.time()
    if holding_mouse:
        mouse_moving = False
    root.after(100, check_movement)

listener = mouse.Listener(on_move=on_move, on_click=on_click)
listener.start()

# --- Tkinter UI
root = tk.Tk()
root.title("Emotion Meter")
canvas = tk.Canvas(root, width=400, height=400, bg='white')
canvas.pack()
cx, cy = 200, 200
r = 150

def draw_meter_background():
    canvas.delete("all")
    canvas.create_oval(cx - r, cy - r, cx + r, cy + r, outline='gray', width=3)
    for angle in angle_list:
        x = cx + r * cos(radians(angle))
        y = cy - r * sin(radians(angle))
        emotion = angle_emotion_map[angle]
        canvas.create_text(x, y, text=emotion, font=("Helvetica", 10))

def update_meter():
    global selected_emotion, certainty_result
    draw_meter_background()
    
    display_angle = locked_angle if locked_angle is not None else needle_angle
    x = cx + r * 0.9 * cos(radians(display_angle))
    y = cy - r * 0.9 * sin(radians(display_angle))
    canvas.create_line(cx, cy, x, y, width=4, fill='red')
    
    selected_emotion, _ = emotion_from_angle(display_angle)
    canvas.create_text(cx, cy + r + 20, text=f"Emotion: {selected_emotion}", font=("Helvetica", 14))
    
    if certainty_result:
        label, score = certainty_result
        canvas.create_text(cx, cy + r + 45, text=f"Certainty: {label}", font=("Helvetica", 12), fill='green')
    elif locked_angle:
        hold_time = time.time() - holding_start_time
        canvas.create_text(cx, cy + r + 45, text=f"Hold time: {hold_time:.1f}s", font=("Helvetica", 12), fill='blue')
    
    root.after(100, update_meter)

update_meter()
check_movement()
root.mainloop()