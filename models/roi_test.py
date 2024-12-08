from ultralytics import YOLO
import cv2
import math
import numpy as np

cap = cv2.VideoCapture(1)
model = YOLO("models/weights/best.pt")

classNames = [
    "backpack", "bench", "handbag", "person", "refrigerator", "Product"
]

# Define a smaller ROI (operation workspace)
roi_x1, roi_y1 = 0, 0  # Top-left corner of the smaller ROI
roi_x2, roi_y2 = 1920, 1080  # Bottom-right corner of the smaller ROI

# Function to extract dominant color in the t-shirt region
def get_tshirt_color(roi):
    # Convert the image to HSV
    hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    
    # Define color ranges (can be adjusted for specific t-shirt colors)
    color_ranges = {
        'Red': ([0, 50, 50], [10, 255, 255]),
        'Green': ([35, 50, 50], [85, 255, 255]),
        'Blue': ([100, 50, 50], [140, 255, 255]),
        'Yellow': ([20, 50, 50], [40, 255, 255]),
        'Black': ([0, 0, 0], [180, 255, 30]),
        'White': ([0, 0, 200], [180, 40, 255])
    }

    # Create a mask for each color and detect the dominant one
    max_color_area = 0
    dominant_color = 'Unknown'
    for color, (lower, upper) in color_ranges.items():
        lower = np.array(lower)
        upper = np.array(upper)
        mask = cv2.inRange(hsv_roi, lower, upper)
        color_area = cv2.countNonZero(mask)

        if color_area > max_color_area:
            max_color_area = color_area
            dominant_color = color

    return dominant_color

# Function to convert color name to BGR value
def get_bgr_color(color_name):
    color_map = {
        'Red': (0, 0, 255),
        'Green': (0, 255, 0),
        'Blue': (255, 0, 0),
        'Yellow': (0, 255, 255),
        'Black': (0, 0, 0),
        'White': (255, 255, 255)
    }
    return color_map.get(color_name, (255, 255, 255))  # Default to white if color not found

# Create a named window and set it to a maximized size
cv2.namedWindow("Webcam", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Webcam", 1920, 1080)  # Set to your desired screen size, or use (0, 0) to maximize

while True:
    success, img = cap.read()
    results = model(img, stream=True, conf=0.7)

    # Draw the ROI rectangle on the frame
    cv2.rectangle(img, (roi_x1, roi_y1), (roi_x2, roi_y2), (0, 255, 0), 2)  # Green ROI border

    for r in results:
        boxes = r.boxes

        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

            # Check if the object is inside the smaller ROI
            if x1 >= roi_x1 and y1 >= roi_y1 and x2 <= roi_x2 and y2 <= roi_y2:
                cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 255), 3)

                confidence = math.ceil((box.conf[0] * 100)) / 100
                cls = int(box.cls[0])

                if classNames[cls] == "person":
                    roi = img[y1:y2, x1:x2]  # Get the region of interest for the person (t-shirt area)
                    tshirt_color = get_tshirt_color(roi)  # Get the dominant t-shirt color
                    print(f"T-shirt Color: {tshirt_color}")  # Display detected t-shirt color
                    
                    # Convert the color name to BGR
                    bgr_color = get_bgr_color(tshirt_color)

                    # Draw bounding box with the t-shirt color
                    cv2.rectangle(img, (x1, y1), (x2, y2), bgr_color, 3)

                    # Display the t-shirt color text
                    cv2.putText(img, f"T-shirt: {tshirt_color}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

                org = [x1, y1]
                font = cv2.FONT_HERSHEY_SIMPLEX
                fontScale = 1
                color = (255, 0, 0)
                thickness = 2

                cv2.putText(img, classNames[cls], org, font, fontScale, color, thickness)

    cv2.imshow('Webcam', img)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
