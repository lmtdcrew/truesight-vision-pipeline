import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
from ultralytics import YOLO

# Paths
data_path = "data/training"
left_path = os.path.join(data_path, "image_2")
right_path = os.path.join(data_path, "image_3")

# KITTI camera calibration — focal length and baseline
FOCAL_LENGTH = 721.5377 # pixels
BASELINE = 0.54 # meters (distance between cameras)
METERS_TO_FEET = 3.28084

# Load stereo pair
left_files = sorted(os.listdir(left_path))
right_files = sorted(os.listdir(right_path))
left_img = cv2.imread(os.path.join(left_path, left_files[0]))
right_img = cv2.imread(os.path.join(right_path, right_files[0]))

# Convert to grayscale for stereo matching
left_gray = cv2.cvtColor(left_img, cv2.COLOR_BGR2GRAY)
right_gray = cv2.cvtColor(right_img, cv2.COLOR_BGR2GRAY)

# Compute disparity map
stereo = cv2.StereoSGBM_create(
    minDisparity=0,
    numDisparities=128,
    blockSize=11,
    P1=8 * 3 * 11 ** 2,
    P2=32 * 3 * 11 ** 2,
    disp12MaxDiff=1,
    uniquenessRatio=10,
    speckleWindowSize=100,
    speckleRange=32
)
disparity = stereo.compute(left_gray, right_gray).astype(np.float32) / 16.0

# Convert disparity to depth in feet
with np.errstate(divide='ignore'):
    depth_meters = np.where(
        disparity > 0,
        (FOCAL_LENGTH * BASELINE) / disparity,
        0
    )
depth_feet = depth_meters * METERS_TO_FEET

# Run YOLO detection
model = YOLO("best.pt")
results = model(left_img, verbose=False)

# Draw boxes with distance on image
output_img = left_img.copy()
for box in results[0].boxes:
    x1, y1, x2, y2 = map(int, box.xyxy[0])
    class_id = int(box.cls[0])
    class_name = model.names[class_id]
    confidence = float(box.conf[0])

    # Get center of box
    cx = (x1 + x2) // 2
    cy = (y1 + y2) // 2

    # Sample depth at center of detection box
    if 0 <= cy < depth_feet.shape[0] and 0 <= cx < depth_feet.shape[1]:
        dist_feet = depth_feet[cy, cx]
    else:
        dist_feet = 0

    # Choose label
    if dist_feet > 0 and dist_feet < 500:
        label = f"{class_name} {confidence:.2f} | {dist_feet:.0f} ft"
    else:
        label = f"{class_name} {confidence:.2f}"

    # Draw box and label
    cv2.rectangle(output_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
    cv2.rectangle(output_img, (x1, y1 - 20), (x1 + len(label) * 8, y1), (0, 255, 0), -1)
    cv2.putText(output_img, label, (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)


# Color depth map
disparity_display = cv2.normalize(
    disparity, None, alpha=0, beta=255,
    norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U
)
depth_colormap = cv2.applyColorMap(disparity_display, cv2.COLORMAP_MAGMA)

# Convert for display
output_rgb = cv2.cvtColor(output_img, cv2.COLOR_BGR2RGB)
depth_rgb = cv2.cvtColor(depth_colormap, cv2.COLOR_BGR2RGB)

# Display
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 5))
ax1.imshow(output_rgb)
ax1.set_title("Detection + Distance (feet)")
ax1.axis("off")
ax2.imshow(depth_rgb)
ax2.set_title("Depth Map (Warm = Close, Cool = Far)")
ax2.axis("off")
plt.suptitle("TrueSight — Combined Pipeline", fontsize=14)
plt.tight_layout()
plt.show()

print("\nCombined Pipeline Complete")