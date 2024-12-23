import tkinter as tk
import threading
from Final_script import run_yolo_camera  # Import YOLO function

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

        # Buttons
        button_frame = tk.Frame(self.window)
        button_frame.pack(pady=10)

        self.start_button = tk.Button(button_frame, text="Start Camera", command=self.start_camera)
        self.start_button.grid(row=0, column=0, padx=5)

        self.stop_button = tk.Button(button_frame, text="Stop Camera", command=self.stop_camera)
        self.stop_button.grid(row=0, column=1, padx=5)

        # Thread and flag for YOLO processing
        self.camera_thread = None
        self.running_flag = {"running": False}  # Dictionary for mutable flag

        # Close handler
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def start_camera(self):
        """Start the YOLO function in a separate thread."""
        if self.running_flag["running"]:
            print("Camera is already running!")
            return

        self.running_flag["running"] = True
        self.camera_thread = threading.Thread(target=run_yolo_camera, args=(self.running_flag,))
        self.camera_thread.start()

    def stop_camera(self):
        """Stop the camera feed."""
        if self.running_flag["running"]:
            print("Stopping the camera...")
            self.running_flag["running"] = False
            if self.camera_thread:
                self.camera_thread.join()  # Wait for the thread to finish
        else:
            print("Camera is not running.")

    def on_closing(self):
        """Handle window closing."""
        self.stop_camera()
        self.window.destroy()
