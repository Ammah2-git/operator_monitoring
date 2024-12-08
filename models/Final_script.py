from ultralytics import YOLO
import cv2
import math

# Initialize the camera and YOLO model
cap = cv2.VideoCapture(0)
model = YOLO("models/weights/best.pt")

# Define class names
classNames = [
    "backpack", "bench", "handbag", "person", "refrigerator", "Product"
]

# Define a smaller ROI (operation workspace)
roi_x1, roi_y1 = 100, 0  # Top-left corner of the smaller ROI
roi_x2, roi_y2 = 600, 1080  # Bottom-right corner of the smaller ROI

# Create a named window and set it to a maximized size
cv2.namedWindow("Webcam", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Webcam", 1920, 1080)  # Set to your desired screen size, or use (0, 0) to maximize

# Main loop
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

                # Add a label to the bounding box
                org = [x1, y1]
                font = cv2.FONT_HERSHEY_SIMPLEX
                fontScale = 1
                color = (255, 0, 0)
                thickness = 2
                cv2.putText(img, classNames[cls], org, font, fontScale, color, thickness)

    # Display the frame
    cv2.imshow('Webcam', img)

    # Exit the loop when 'q' is pressed
    if cv2.waitKey(1) == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
