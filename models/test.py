from ultralytics import YOLO
import cv2
import math
cap = cv2.VideoCapture(1)

# model
model = YOLO("models/weights/best.pt" )

classNames = [
    "backpack", "bench", "handbag", "person", "refrigerator", "Product"
]

while True:
    success, img = cap.read()
    results = model(img, stream=True, conf = 0.7)

    for r in results:
        boxes = r.boxes

        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2) 

            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 255), 3)

            confidence = math.ceil((box.conf[0]*100))/100
            print(f"Confidence ---> {confidence}")

            cls = int(box.cls[0])
            print(f"Class name --> {classNames[cls]}")

            # object details
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