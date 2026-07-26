# 🟢 Green Invisibility Cloak — Real-Time Background Substitution with OpenCV

Turn any green cloth into a real-life "invisibility cloak" using nothing but your webcam and Python. Inspired by the classic Harry Potter cloak trick, rebuilt with a production-ready, threaded OpenCV pipeline optimized for smooth FPS.

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-5C3EE8?logo=opencv&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

---

## ✨ Features

- 🎥 **Real-time webcam processing** with a threaded capture pipeline for smooth, non-blocking FPS
- 🟢 **Green-color detection** using an HSV mask tuned to work across common lighting conditions
- 🧠 **Noise-robust masking** — connected-component filtering removes small false-positive blobs
- 🎬 **Live edge feathering** for a natural, non-jagged cloak effect instead of a hard cutout
- 📊 **On-screen FPS counter** (exponentially smoothed) to monitor performance live
- 🔴 **Built-in screen recording** — save your invisibility effect straight to `.mp4`
- 📸 **One-key screenshots**
- 🔁 **Re-capturable background** — no need to restart the script if lighting or framing changes

---

## 🎯 How It Works

1. The script captures ~60 background frames (median-blended for stability) while you're out of frame.
2. Every subsequent frame is converted to HSV and masked against a tuned green color range.
3. Morphological operations (open + dilate) and connected-component filtering clean up the mask, removing noise.
4. Pixels inside the mask are replaced with the corresponding background pixels — with feathered edges — producing the "invisible" effect.
5. A background thread continuously grabs camera frames so the main loop never blocks on I/O, keeping FPS smooth.

---

## 📦 Requirements

- Python 3.8+
- A webcam
- A solid green cloth (matte fabric works best — avoid shiny/reflective material)

---

## 🛠️ Installation

```bash
git clone https://github.com/SAILESHKUMARSAINI/green-invisibility-cloak.git
cd green-invisibility-cloak
pip3 install opencv-python numpy --break-system-packages
```

> **Note:** `--break-system-packages` is only needed on systems (like newer macOS/Homebrew Python) that block system-wide pip installs by default. On most systems, a plain `pip3 install opencv-python numpy` works fine.

---

## ▶️ Usage

```bash
python3 green_cloak.py
```

1. When the script starts, **step out of frame** — it needs a clean background.
2. Once you see `[INFO] Background captured.` in the terminal, step back in with your green cloth.
3. Wherever the cloth covers you, the background will show through instead — congratulations, you're invisible. 🪄

### Controls

| Key | Action |
|-----|--------|
| `q` | Quit the application |
| `b` | Re-capture the background (step out of frame first) |
| `s` | Save a screenshot (`.png`) |
| `r` | Start / stop recording to an `.mp4` file |

---

## ⚙️ Configuration

Key tunables live at the top of `green_cloak.py`:

```python
LOWER_GREEN = np.array([35, 40, 40])
UPPER_GREEN = np.array([90, 255, 255])

BG_CAPTURE_FRAMES = 60
MIN_BLOB_AREA = 1000

FRAME_WIDTH = 640
FRAME_HEIGHT = 360
```

- **`LOWER_GREEN` / `UPPER_GREEN`** — HSV range for detecting your cloth. If detection is patchy, adjust these.
- **`MIN_BLOB_AREA`** — minimum pixel area to count as "cloak" (filters out small noisy detections).
- **`FRAME_WIDTH` / `FRAME_HEIGHT`** — lower resolution = higher FPS. Raise these for more visual quality if your machine can handle it.

---

## 🚀 Performance Notes

This isn't the naive tutorial version — it's built to actually run smoothly:

- **Threaded camera capture** decouples frame grabbing from processing, so I/O never stalls rendering.
- **Reduced default resolution** (640×360) cuts per-frame pixel work by ~4x compared to 720p.
- **Single-pass morphology** and a pre-allocated kernel avoid redundant computation every frame.
- **Buffer size = 1** on the capture stream prevents stale frames from queueing and causing lag.

---

## 🖼️ Demo

*(Add a GIF or screenshot of the effect here once recorded — you can generate one using the built-in `r` recording key.)*

---

## 🧩 Tech Stack

- **Python 3**
- **OpenCV** — video capture, color space conversion, masking, morphology
- **NumPy** — array operations and frame math

---

## 📌 Possible Future Improvements

- [ ] Multi-color support (red / blue / green presets)
- [ ] Live HSV calibration UI with trackbars
- [ ] GPU-accelerated masking for higher resolutions
- [ ] Web-based version using WebRTC + OpenCV.js

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you'd like to change.

---

## 📄 License

This project is licensed under the MIT License — feel free to use, modify, and share.

---

## 👤 Author

**Sailesh Kumar Saini**
MCA (Data Science) | IEEE Student Member | Building AI/CV projects for placements

- GitHub: [@SAILESHKUMARSAINI](https://github.com/SAILESHKUMARSAINI)
