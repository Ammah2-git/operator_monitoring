import tkinter as tk
import cv2
import pandas as pd
import os
from camera_module import CameraModule  # Ensure this module is implemented


class WideAngleCameraInterface:
    def __init__(self):
        # Create a new Toplevel window
        self.window = tk.Toplevel()
        self.window.title("Wide-Angle Camera Interface")

        # Create a frame for the video feed
        self.video_frame = tk.Frame(self.window, bg="black", bd=2, relief="ridge")
        self.video_frame.pack(pady=10)
        self.video_label = tk.Label(self.video_frame, text="Video Feed", font=("Arial", 14), fg="white", bg="black")
        self.video_label.pack()

        # Camera module instance
        self.camera = CameraModule()

        # Start and stop buttons
        button_frame = tk.Frame(self.window)
        button_frame.pack(pady=10)
        self.start_button = tk.Button(button_frame, text="Start Camera", command=self.start_camera)
        self.start_button.grid(row=0, column=0, padx=5)

        self.stop_button = tk.Button(button_frame, text="Stop Camera", command=self.stop_camera)
        self.stop_button.grid(row=0, column=1, padx=5)

        self.roi_button = tk.Button(button_frame, text="Select ROI", command=self.select_roi)
        self.roi_button.grid(row=0, column=2, padx=5)

        # Handle window closing
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def start_camera(self):
        """Start the camera feed."""
        self.camera.start_feed(self.video_label)

    def stop_camera(self):
        """Stop the camera feed and reset the video label."""
        self.camera.stop_feed()
        self.video_label.config(image='', text="Video Feed", bg="black", fg="white")

    def select_roi(self):
        """Open ROI selection interface."""
        roi_x1, roi_y1, roi_x2, roi_y2 = select_roi()
        if roi_x1 is not None:
            print(f"Selected ROI: Top-left ({roi_x1}, {roi_y1}), Bottom-right ({roi_x2}, {roi_y2})")
            self.save_roi_to_csv(roi_x1, roi_y1, roi_x2, roi_y2)
        else:
            print("No ROI selected.")
    
    def save_roi_to_csv(self, x1, y1, x2, y2, file_name="selected_roi.csv"):
        # Create a DataFrame for the new ROI
        new_roi = pd.DataFrame([{"TopLeft_X": x1, "TopLeft_Y": y1, "BottomRight_X": x2, "BottomRight_Y": y2}])

        try:
            # Append to the existing CSV file
            new_roi.to_csv(file_name, mode='a', index=False, header=not os.path.exists(file_name))
        except Exception as e:
            print(f"Error saving ROI to CSV: {e}")
        else:
            print(f"ROI saved to {file_name}")
        
    def on_closing(self):
        """Release camera resources before closing."""
        self.camera.stop_feed()
        self.window.destroy()


def select_roi(camera_index=0, resolution=(1920, 1080)): 
    """
    Opens the camera, displays the feed, allows ROI selection, and shuts down the camera afterward.
    Returns the top-left and bottom-right coordinates of the selected ROI.
    """
    roi_coords = [-1, -1, -1, -1]  # Top-left and bottom-right coordinates
    drawing = [False]  # State of drawing (mutable to use in the nested function)

    def draw_roi(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            drawing[0] = True
            roi_coords[0], roi_coords[1] = x, y
        elif event == cv2.EVENT_MOUSEMOVE and drawing[0]:
            roi_coords[2], roi_coords[3] = x, y
        elif event == cv2.EVENT_LBUTTONUP:
            drawing[0] = False
            roi_coords[2], roi_coords[3] = x, y

    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return None, None, None, None

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])

    cv2.namedWindow("Select ROI", cv2.WINDOW_NORMAL)
    cv2.setMouseCallback("Select ROI", draw_roi)

    while True:
        success, frame = cap.read()
        if not success:
            break

        if roi_coords[0] != -1:
            cv2.rectangle(frame, (roi_coords[0], roi_coords[1]), (roi_coords[2], roi_coords[3]), (0, 255, 0), 2)

        cv2.imshow("Select ROI", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return tuple(roi_coords) if roi_coords[0] != -1 else (None, None, None, None)
