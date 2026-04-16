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

## April 11, 2026

### Session Summary
- Completed Phase 2 — YOLOv8 fine-tuning with full 36,000 image dataset
- Previous runs used only 3,794 training images due to corrupted Kaggle upload
- Fixed with 7-Zip re-archive, verified 36,000 train images before upload
- Final training run: 20 epochs, 2.492 hours, Tesla T4

### Results (best.pt v2 — full dataset)
- mAP50: 0.4708 | mAP50-95: 0.3347
- fighter-jet: 0.447 (was 0.0) — fixed by full dataset
- tank: 0.622 (was 0.058) — fixed by full dataset
- soldier: 0.689 | pistol: 0.684 | helicopter: 0.737
- drone: 0.407 — confusion with civilian class, needs cleaner training data

### best.pt integrated
- Replaced YOLO('yolov8n.pt') with YOLO('best.pt') in combined_pipeline.py
- Pipeline runs clean, depth map + military detection confirmed working

### Next Steps
- Record demo video of combined_pipeline.py with best.pt
- Begin Phase 3 — BNO085 IMU Visualizer (needs Teensy wiring)

## April 13, 2026

### Phase 3 — BNO085 IMU Visualizer

**Hardware:**
- BNO085 (GY-BNO08X) wired to Teensy 4.1 via I2C (VCC→3.3V, GND→G, SCL→pin19, SDA→pin18)
- Confirmed I2C address 0x4B via scanner sketch
- New micro-USB data cable purchased (Best Buy) to resolve upload issue
- Teensy Loader standalone app required for Arduino IDE 2.x compatibility

**Software:**
- SparkFun BNO08x library installed via ZIP
- Example_01_RotationVector sketch uploaded with BNO08X_ADDR=0x4B, INT=-1, RST=-1
- imu_visualizer.py written — pygame + PyOpenGL quaternion 3D visualizer
- Correct OpenGL column-major matrix implemented (verified via songho.ca)
- Axis mapping resolved: rel[1], -rel[3], rel[2] for pitch/yaw/roll
- Serial buffer drain added to eliminate visualizer lag
- Tare implemented in raw BNO frame before axis remapping

**Status:** Phase 3 COMPLETE. IMU tracking confirmed accurate on all 3 axes.

**Next:** Reference Guide #5 for imu_visualizer.py, then Phase 4 mmWave radar visualization.

## April 15, 2026

### Phase 4 — IWR6843AOP mmWave Radar — COMPLETE

**What was built:**
- Diagnosed IWR6843AOP as CP2105-based (Silicon Labs, VID 10C4 PID EA70) — not XDS110
- Installed CP210x VCP drivers — COM4 (CFG/Enhanced) and COM5 (Data/Standard) enumerated
- Identified S3 switch (back of board) as SOP2 boot mode control — S2 is peripheral routing only
- Flashed mmWave demo firmware via UniFlash 9.5.0: xwr68xx_mmw_demo.bin
- Confirmed live point cloud in TI mmWave Demo Visualizer
- Wrote radar_visualizer.py — live 2D+3D PyQtGraph visualizer reading COM5 at 921600 baud

**Key learnings:**
- IWR6843AOP has no onboard XDS110 — serial flash only via CP2105
- Flash mode: S3 ON. Functional mode: S3 OFF. S1/S2 unchanged between modes
- UniFlash must use Enhanced COM port (COM4) for flashing

**Status:** Phase 4 COMPLETE. Phase 5 blocked on ArduCam B0492N (~$300).

