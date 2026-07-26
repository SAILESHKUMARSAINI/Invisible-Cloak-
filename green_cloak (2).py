"""
Green Invisibility Cloak
-------------------------
Simplified, green-only version. Detects a green cloth in the webcam feed
and replaces it with the pre-captured background, creating an
"invisible" effect. No color switching, no calibration UI clutter —
just green, tuned to be forgiving across common lighting conditions,
and optimized to keep FPS smooth.

Usage:
    python3 green_cloak.py

Controls (while the window is focused):
    q - quit
    b - recapture background (step out of frame first)
    s - save a screenshot
"""

import threading
import time
import sys

import cv2
import numpy as np

# --------------------------------------------------------------------------- #
# Green HSV range — wide enough to catch most green fabrics (light/dark,
# slightly yellow-green or blue-green) under normal indoor lighting.
# If it's still not catching your cloth, run the calibration snippet
# at the bottom of this file (see `calibrate()`).
# --------------------------------------------------------------------------- #
LOWER_GREEN = np.array([35, 40, 40])
UPPER_GREEN = np.array([90, 255, 255])

BG_CAPTURE_FRAMES = 60
MIN_BLOB_AREA = 1000

# Capture at a lower resolution — this is the single biggest FPS lever.
# 1280x720 forces cv2 to touch ~4x more pixels than 640x360 every frame,
# for masking work that doesn't need the extra detail.
FRAME_WIDTH = 640
FRAME_HEIGHT = 360


class CameraStream:
    """
    Grabs frames on a background thread so `cap.read()`'s blocking I/O
    never stalls the processing/render loop. Without this, FPS is capped
    by (capture time + processing time) instead of just processing time.
    """

    def __init__(self, index=0, width=FRAME_WIDTH, height=FRAME_HEIGHT):
        self.cap = cv2.VideoCapture(index)
        if not self.cap.isOpened():
            raise RuntimeError("Could not open camera. Check permissions/connection.")
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # don't let stale frames queue up

        ret, frame = self.cap.read()
        if not ret:
            raise RuntimeError("Camera opened but returned no frame.")
        self.frame = np.flip(frame, axis=1)
        self.lock = threading.Lock()
        self.running = True
        self.thread = threading.Thread(target=self._update, daemon=True)
        self.thread.start()

    def _update(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                continue
            frame = np.flip(frame, axis=1)
            with self.lock:
                self.frame = frame

    def read(self):
        with self.lock:
            return self.frame.copy()

    def release(self):
        self.running = False
        self.thread.join(timeout=1)
        self.cap.release()


def read_frame(stream):
    return stream.read()



def capture_background(stream):
    print(f"[INFO] Capturing background in {BG_CAPTURE_FRAMES} frames — step OUT of frame now.")
    time.sleep(2)  # give the user time to get out of frame
    samples = []
    for _ in range(BG_CAPTURE_FRAMES):
        samples.append(read_frame(stream).astype(np.float32))
        time.sleep(0.01)  # spread reads out slightly so we don't grab duplicate frames
    bg = np.median(np.stack(samples), axis=0).astype(np.uint8)
    print("[INFO] Background captured.")
    return bg


_KERNEL = np.ones((5, 5), np.uint8)  # module-level: don't reallocate every frame


def build_green_mask(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # A 5x5 blur is enough to denoise and is noticeably cheaper than 11x11.
    blur = cv2.GaussianBlur(hsv, (5, 5), 0)
    mask = cv2.inRange(blur, LOWER_GREEN, UPPER_GREEN)

    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, _KERNEL, iterations=1)
    mask = cv2.dilate(mask, _KERNEL, iterations=1)

    # Remove small noisy blobs, keep only big enough regions (the cloth).
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask)
    clean = np.zeros_like(mask)
    for i in range(1, num_labels):
        if stats[i, cv2.CC_STAT_AREA] > MIN_BLOB_AREA:
            clean[labels == i] = 255
    return clean


def apply_cloak(frame, mask, background):
    mask_blur = cv2.GaussianBlur(mask, (5, 5), 0)
    mask_3ch = cv2.merge([mask_blur] * 3).astype(np.float32) / 255.0
    out = frame.astype(np.float32) * (1 - mask_3ch) + background.astype(np.float32) * mask_3ch
    return out.astype(np.uint8)


def main():
    try:
        stream = CameraStream()
    except RuntimeError as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

    try:
        background = capture_background(stream)
        print("[INFO] Running. Press 'q' to quit, 'b' to recapture background, 's' to screenshot.")

        fps_smoothed = 0.0
        prev_time = time.time()

        while True:
            frame = read_frame(stream)
            mask = build_green_mask(frame)
            output = apply_cloak(frame, mask, background)

            # FPS calculation, exponentially smoothed so the number doesn't jitter.
            now = time.time()
            instant_fps = 1.0 / max(now - prev_time, 1e-6)
            fps_smoothed = fps_smoothed * 0.9 + instant_fps * 0.1
            prev_time = now
            cv2.putText(output, f"FPS: {fps_smoothed:.1f}", (10, 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            # Optional debug view: uncomment to see the raw mask
            # cv2.imshow("Mask", mask)

            cv2.imshow("Green Invisibility Cloak", output)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("[INFO] Quitting.")
                break
            elif key == ord('b'):
                background = capture_background(stream)
            elif key == ord('s'):
                fname = f"screenshot_{int(time.time())}.png"
                cv2.imwrite(fname, output)
                print(f"[INFO] Saved {fname}")

    finally:
        stream.release()
        cv2.destroyAllWindows()
        print("[INFO] Camera released. Bye!")


if __name__ == "__main__":
    main()
