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

## April 8, 2026

### Session Summary
- Colab GPU quota exhausted mid-training (epoch 20, 57% complete)
- best.pt lost — /content/ directory wiped on runtime reset
- Migrated training pipeline from Colab to Kaggle
- Resolved Kaggle phone verification, GPU access, and internet permissions
- Uploaded TrueSight V1 dataset (41,136 images) to Kaggle as truesight-data
- Retrained YOLOv8n — 20 epochs, 2.469 hours on Tesla T4

### Results (best.pt)
- mAP50: 0.487
- mAP50-95: 0.347
- Strong classes: explosion (0.923), shotgun (0.920), drone (0.880), civilian (0.824)
- Weak classes: fighter-jet (0.0), ground-transport (0.0), tank (0.058)

### Root Cause — Weak Classes
- Training only saw 12 fighter-jet instances vs 2,940 in Roboflow
- Dataset upload to Kaggle was likely truncated — only ~3,794 training images used instead of 36,046
- Fix: re-download V1 fresh from Roboflow, verify count, re-upload, retrain tomorrow

### Next Steps
- Verify train/images has 36,046 files in fresh Roboflow export
- Delete current Kaggle dataset, upload clean zip, retrain
- Swap best.pt into combined_pipeline.py and test
- Record combined_pipeline.py demo video once best.pt v2 is integrated