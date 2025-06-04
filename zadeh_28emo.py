import tkinter as tk
from math import sin, cos, radians
from pynput import mouse
import time

# --- 28 Circumplex Emotions from Russell's model
emotion_list = [
    "Pleasant", "Happy", "Elated", "Excited", "Aroused", "Alert", "Tense",
    "Nervous", "Stressed", "Upset", "Unpleasant", "Sad", "Depressed",
    "Bored", "Tired", "Sleepy", "Drowsy", "Calm", "Relaxed", "Serene",
    "Content", "Satisfied", "Glad", "Cheerful", "Lively", "Delighted",
    "Joyful"
]

num_emotions = len(emotion_list)
angle_step = 360 / num_emotions
emotion_angle_map = {emotion: int(i * angle_step) % 360 for i, emotion in enumerate(emotion_list)}
angle_emotion_map = {v: k for k, v in emotion_angle_map.items()}
angle_list = sorted(angle_emotion_map.keys())

# --- Certainty labels
def get_certainty_label(hold_time):
    if hold_time >= 15:
        return "🌟 very sure", 1.0
    elif hold_time >= 7:
        return "✅ sure", 0.66
    else:
        return "🤔 uncertain", 0.33

# --- Find nearest emotion
def emotion_from_angle(angle):
    closest_angle = min(angle_list, key=lambda x: abs(x - angle))
    return angle_emotion_map[closest_angle], closest_angle

# --- State variables
last_move_time = time.time()
current_pos = (0, 0)
needle_angle = 0
selected_emotion = None
holding_start_time = None
certainty_result = None
holding_mouse = False
mouse_moving = False
locked_angle = None

# --- Mouse events
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

def check_movement():
    global mouse_moving, locked_angle, holding_start_time
    if holding_mouse and not mouse_moving and locked_angle is None:
        locked_angle = needle_angle
        holding_start_time = time.time()
    if holding_mouse:
        mouse_moving = False
    root.after(100, check_movement)

from pynput import mouse
listener = mouse.Listener(on_move=on_move, on_click=on_click)
listener.start()

# --- GUI setup
root = tk.Tk()
root.title("🎯 Z-Mouse Emotion Meter")
canvas = tk.Canvas(root, width=550, height=550, bg='#f8f9fa', highlightthickness=0)
canvas.pack()
cx, cy = 275, 275
r = 200

def draw_meter_background():
    canvas.delete("all")
    # Outer circle
    canvas.create_oval(cx - r, cy - r, cx + r, cy + r, outline='#6c757d', width=4)

    # Label all emotions around the circle
    for angle in angle_list:
        angle_rad = radians(angle)
        label_x = cx + (r - 20) * cos(angle_rad)
        label_y = cy - (r - 20) * sin(angle_rad)
        emotion = angle_emotion_map[angle]
        canvas.create_text(label_x, label_y, text=emotion, font=("Helvetica", 9, "bold"), fill="#343a40")

def update_meter():
    global selected_emotion, certainty_result
    draw_meter_background()

    # Draw needle
    display_angle = locked_angle if locked_angle is not None else needle_angle
    x = cx + r * 0.85 * cos(radians(display_angle))
    y = cy - r * 0.85 * sin(radians(display_angle))
    canvas.create_line(cx, cy, x, y, width=4, fill='#e63946', capstyle=tk.ROUND)

    # Selected emotion
    selected_emotion, _ = emotion_from_angle(display_angle)
    canvas.create_text(cx, cy + r + 30, text=f"Emotion: {selected_emotion}", font=("Helvetica", 14, "bold"), fill="#212529")

    # Certainty or hold time
    if certainty_result:
        label, score = certainty_result
        canvas.create_text(cx, cy + r + 55, text=f"Certainty: {label}", font=("Helvetica", 12), fill="#198754")
    elif locked_angle:
        hold_time = time.time() - holding_start_time
        canvas.create_text(cx, cy + r + 55, text=f"Hold time: {hold_time:.1f}s", font=("Helvetica", 12), fill="#0d6efd")

    root.after(100, update_meter)

# Run GUI
update_meter()
check_movement()
root.mainloop()
