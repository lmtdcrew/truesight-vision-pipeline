# TrueSight Development Log

---

## April 6, 2026

**Environment Setup — COMPLETE**
- Installed Python 3.11.9, Git 2.53.0, VS Code on Windows 10
- Installed all dependencies: torch, torchvision, opencv-python, numpy,
  matplotlib, ultralytics, open3d
- Created GitHub repo: truesight-vision-pipeline
- Cloned repo locally to C:\Users\broke\Documents\truesight-vision-pipeline

**KITTI Dataset — COMPLETE**
- Registered for KITTI Vision Benchmark Suite
- Downloaded and extracted KITTI Stereo 2015 dataset (2GB) + calibration files
- Data structure confirmed: data/training and data/testing folders present

**load_kitti.py — COMPLETE**
- Wrote first script to load and display KITTI stereo image pairs
- Both left and right camera feeds displaying correctly side by side
- Confirmed stereo pair offset visible — foundation for depth estimation ready

**Next:**
- Write stereo depth estimation script using RAFT-Stereo or CREStereo
- Add YOLOv8 object detection overlay on left camera frame
- Build combined display showing stereo + depth map + detection boxes

## April 7, 2026

**combined_pipeline.py — COMPLETE**
- Built combined pipeline merging stereo depth estimation + YOLOv8 object detection
- Detection boxes showing object class, confidence score, and distance in feet
- Depth map rendered side by side using MAGMA colormap
- Distance calculation: depth = (focal_length x baseline) / disparity, converted to feet
- All three scripts (load_kitti, depth_estimation, object_detection, combined_pipeline) working

**Next:**
- Reference Guide #4 for combined_pipeline.py
- Begin YOLOv8 fine-tuning on Roboflow/Colab
- Update LinkedIn with pipeline progress post