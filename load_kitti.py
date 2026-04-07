import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

#path to kitti stereo images
data_path = "data/training"
left_path = os.path.join(data_path, "image_2")
right_path = os.path.join(data_path, "image_3")

#load first stereo pair
left_files = sorted(os.listdir(left_path))
right_files = sorted(os.listdir(right_path))

print(f"Found {len(left_files)} stereo pairs")

#load first pair
left_img = cv2.imread(os.path.join(left_path, left_files [0]))
right_img = cv2.imread(os.path.join(right_path, right_files[0]))

#convert to RGB for display
left_rgb = cv2.cvtColor(left_img, cv2.COLOR_BGR2RGB)
right_rgb = cv2.cvtColor(right_img,cv2.COLOR_BGR2RGB)

#display
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
ax1.imshow(left_rgb)
ax1.set_title("Left Camera")
ax1.axis("off")
ax2.imshow(right_rgb)
ax2.set_title("Right Camera")
ax2.axis("off")
plt.suptitle("KITTI Stereo Pair - TrueSight Vision Pipeline", fontsize=14)
plt.tight_layout()
plt.show()

print("Success - Stereo Pair Loaded and Displayed")