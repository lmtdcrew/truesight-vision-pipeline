import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
from ultralytics import YOLO

# Paths
data_path = "data/training"
left_path = os.path.join(data_path, "image_2")

# Load first left image
left_files = sorted(os.listdir(left_path))
left_img = cv2.imread(os.path.join(left_path, left_files[0]))
left_rgb = cv2.cvtColor(left_img, cv2.COLOR_BGR2RGB)

# Load YOLOv8 nano model — downloads automatically first run
model = YOLO("yolov8n.pt")

# Run detection
results = model(left_img, verbose=False)

# Draw detection boxes on image
annotated = results[0].plot()
annotated_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)

# Print what was detected
print("\nDetected objects:")
for box in results[0].boxes:
    class_id = int(box.cls[0])
    class_name = model.names[class_id]
    confidence = float(box.conf[0])
    print(f" {class_name}: {confidence:.2f} confidence")

# Display
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
ax1.imshow(left_rgb)
ax1.set_title("Original Left Camera")
ax1.axis("off")
ax2.imshow(annotated_rgb)
ax2.set_title("YOLOv8 Object Detection")
ax2.axis("off")
plt.suptitle("TrueSight — Object Detection Pipeline", fontsize=14)
plt.tight_layout()
plt.show()

print("\nDetection Complete")