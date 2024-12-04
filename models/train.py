from roboflow import Roboflow
rf = Roboflow(api_key="cUtCHmmTz9cbKFKiqGFY")
project = rf.workspace("abc-d9ezq").project("package-v2")
version = project.version(5)
dataset = version.download("yolov8")

from ultralytics import YOLO
model = YOLO("yolov8n.pt")

results = model.train(data="/content/Package-V2-5/data.yaml", epochs=1000)