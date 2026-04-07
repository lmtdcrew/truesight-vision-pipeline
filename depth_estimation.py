import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

# Paths
data_path = "data/training"
left_path = os.path.join(data_path, "image_2")
right_path = os.path.join(data_path, "image_3")

# Load stereo pair
left_files = sorted(os.listdir(left_path))
right_files = sorted(os.listdir(right_path))

left_img = cv2.imread(os.path.join(left_path, left_files[0]))
right_img = cv2.imread(os.path.join(right_path, right_files[0]))

# Convert to grayscale for stereo matching
left_gray = cv2.cvtColor(left_img, cv2.COLOR_BGR2GRAY)
right_gray = cv2.cvtColor(right_img, cv2.COLOR_BGR2GRAY)

# Create stereo matcher
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

# Compute disparity map
disparity = stereo.compute(left_gray, right_gray).astype(np.float32) / 16.0

# Normalize for display
disparity_display = cv2.normalize(
disparity, None, alpha=0, beta=255,
norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U
)

# Apply color map — closer = warmer color, farther = cooler
depth_colormap = cv2.applyColorMap(disparity_display, cv2.COLORMAP_MAGMA)
depth_colormap_rgb = cv2.cvtColor(depth_colormap, cv2.COLOR_BGR2RGB)
left_rgb = cv2.cvtColor(left_img, cv2.COLOR_BGR2RGB)

# Display
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
ax1.imshow(left_rgb)
ax1.set_title("Left Camera")
ax1.axis("off")
ax2.imshow(depth_colormap_rgb)
ax2.set_title("Depth Map (Warm = Close, Cool = Far)")
ax2.axis("off")
plt.suptitle("TrueSight — Stereo Depth Estimation", fontsize=14)
plt.tight_layout()
plt.show()

print("Depth Estimation Complete")