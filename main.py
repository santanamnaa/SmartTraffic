import cv2
import numpy as np
from time import sleep
import concurrent.futures
import tkinter as tk
from PIL import Image, ImageTk

min_width = 190
min_height = 240
offset = 6
line_position = 550
delay = 60
detected = []
cars = 0
cap = None
subtraction = None

def get_center(x, y, w, h):
    x1 = int(w / 2)
    y1 = int(h / 2)
    cx = x + x1
    cy = y + y1
    return cx, cy

def detect_objects(frame):
    global detected, cars
    grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(grey, (3, 3), 5)
    img_sub = subtraction.apply(blur)
    dilate = cv2.dilate(img_sub, np.ones((5, 5)))
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    dilated = cv2.morphologyEx(dilate, cv2.MORPH_CLOSE, kernel)
    dilated = cv2.morphologyEx(dilated, cv2.MORPH_CLOSE, kernel)
    contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for (i, c) in enumerate(contours):
        (x, y, w, h) = cv2.boundingRect(c)
        validate_contour = (w >= min_width) and (h >= min_height)
        if not validate_contour:
            continue

        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        center = get_center(x, y, w, h)
        detected.append(center)
        cv2.circle(frame, center, 4, (0, 0, 255), -1)

        for (x, y) in detected:
            if y < (line_position + offset) and y > (line_position - offset):
                cars += 1
                detected.remove((x, y))

    cv2.putText(frame, "Vehicle Count: " + str(cars), (450, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 5)
    cv2.line(frame, (165, line_position), (1300, line_position), (255, 127, 0), 3)
    return frame

def start_detection():
    global cap, subtraction
    cap = cv2.VideoCapture('video.mp4')
    subtraction = cv2.createBackgroundSubtractorMOG2()
    detect_from_video()

def reset_gui():
    global detected, cars
    detected = []
    cars = 0
    show_gui()

def stop_detection():
    global cap
    if cap is not None:
        cap.release()
    cv2.destroyAllWindows()

def close_program():
    stop_detection()
    root.quit()

def show_gui():
    global root
    root = tk.Tk()
    root.title("Traffic Light Detection")
    root.geometry("800x600")

    title_label = tk.Label(root, text="Traffic Light", font=("Arial", 36))
    title_label.pack(pady=30)

    main_frame = tk.Frame(root)
    main_frame.pack(expand=True)

    red_light_img = Image.open("red_light_image.png")
    red_light_img = red_light_img.resize((350, 300))
    red_light_img = ImageTk.PhotoImage(red_light_img)
    red_light_label = tk.Label(main_frame, image=red_light_img)
    red_light_label.image = red_light_img
    red_light_label.pack(pady=(20, 0))

    video_frame = tk.Frame(main_frame)
    video_frame.pack()

    start_button = tk.Button(video_frame, text="Start", font=("Arial", 24), command=start_detection)
    start_button.grid(row=0, column=0, padx=10, pady=(10, 20))

    stop_button = tk.Button(video_frame, text="Stop", font=("Arial", 24), command=close_program)
    stop_button.grid(row=0, column=1, padx=10, pady=(10, 20))

    root.protocol("WM_DELETE_WINDOW", close_program)
    root.mainloop()

def detect_from_video():
    global root
    while True:
        ret, frame1 = cap.read()
        if not ret:
            break

        time_interval = float(1 / delay)
        sleep(time_interval)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            frame_processed = executor.submit(detect_objects, frame1).result()

        cv2.imshow("Original Video", frame_processed)
        if cv2.waitKey(1) == 27:
            break

    cv2.destroyAllWindows()
    cap.release()

show_gui()