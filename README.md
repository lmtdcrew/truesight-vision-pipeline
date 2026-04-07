# TrueSight Vision Pipeline

Wearable edge AI situational awareness system inspired by Anduril's Eagle Eye.
Built by Noah McNabb | Palm Beach State College — Applied AI

---

## What This Is

TrueSight is a personal autonomous situational awareness system I am building from scratch.
The helmet-mounted display combines stereo computer vision, 60GHz mmWave radar, and
real-time AI inference on an NVIDIA Jetson Orin Nano 8GB to produce an Eagle Eye-style
HUD overlay — depth maps, object detection, and sensor fusion alerts rendered through
a dual-OLED FPV display.

This repository contains the software pipeline developed for TrueSight's vision system.

---

## System Architecture

- **Compute:** NVIDIA Jetson Orin Nano 8GB (JetPack 6.2.2)
- **Cameras:** Arducam B0492N — 2.3MP stereo AR0234 global shutter, synchronized
- **Radar:** TI IWR6843AOP 60GHz mmWave EVM
- **IMU:** BNO085 9-DOF
- **Display:** Skyzone Sky04X Pro dual-OLED FPV mask via DisplayPort → Mini HDMI
- **Platform:** Custom helmet mount + tactical vest carry system

---

## Pipeline Phases

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | KITTI stereo depth pipeline | 🔄 In Progress |
| 2 | YOLOv8 object detection fine-tuning | ⬜ Not Started |
| 3 | BNO085 IMU visualizer | ⬜ Not Started |
| 4 | mmWave radar point cloud visualization | ⬜ Not Started |
| 5 | ROS2 multi-sensor fusion demo | ⬜ Not Started |
| 6 | ArduPilot SITL drone telemetry dashboard | ⬜ Not Started |

---

## Current Scripts

- `load_kitti.py` — Loads and displays stereo image pairs from the KITTI Stereo 2015 dataset

---

## Development Environment

- Python 3.11.9
- PyTorch, OpenCV, Ultralytics YOLOv8, Open3D, NumPy, Matplotlib
- Windows 10 (development) → NVIDIA Jetson Orin Nano (deployment)

---

## Goals

Build a functional prototype of a wearable autonomous situational awareness system
demonstrating stereo depth estimation, real-time object detection, and mmWave radar
fusion on edge AI hardware — as a foundation for future defense-tech work.

---

*This project is under active development. Updates pushed regularly.*
