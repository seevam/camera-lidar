#!/usr/bin/env python3
"""
Camera Test Script - Test camera in different lighting conditions
Shows real-time lighting metrics and adjustments
"""

import cv2
import numpy as np
import sys

class CameraLightingTest:
    def __init__(self, camera_id=0):
        self.camera_id = camera_id
        self.cap = None

    def initialize_camera(self):
        """Initialize camera with various settings"""
        print("[INFO] Initializing camera...")
        self.cap = cv2.VideoCapture(self.camera_id)

        # Set resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)

        if not self.cap.isOpened():
            print("[ERROR] Failed to open camera!")
            return False

        print("[INFO] Camera opened successfully")
        print(f"[INFO] Resolution: {int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
        print(f"[INFO] FPS: {int(self.cap.get(cv2.CAP_PROP_FPS))}")
        return True

    def analyze_lighting(self, frame):
        """Analyze lighting conditions of frame"""
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Calculate metrics
        mean_brightness = np.mean(gray)
        std_brightness = np.std(gray)
        min_brightness = np.min(gray)
        max_brightness = np.max(gray)

        # Calculate histogram
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])

        # Determine lighting condition
        if mean_brightness < 50:
            condition = "Very Dark"
            color = (0, 0, 255)  # Red
        elif mean_brightness < 100:
            condition = "Dark"
            color = (0, 128, 255)  # Orange
        elif mean_brightness < 150:
            condition = "Good"
            color = (0, 255, 0)  # Green
        elif mean_brightness < 200:
            condition = "Bright"
            color = (0, 255, 255)  # Yellow
        else:
            condition = "Very Bright"
            color = (255, 255, 255)  # White

        # Calculate contrast
        contrast = std_brightness
        if contrast < 30:
            contrast_level = "Low"
        elif contrast < 60:
            contrast_level = "Medium"
        else:
            contrast_level = "High"

        return {
            'mean': mean_brightness,
            'std': std_brightness,
            'min': min_brightness,
            'max': max_brightness,
            'condition': condition,
            'contrast': contrast,
            'contrast_level': contrast_level,
            'color': color,
            'histogram': hist
        }

    def apply_enhancements(self, frame, mode='none'):
        """Apply various image enhancements"""
        if mode == 'none':
            return frame

        elif mode == 'brightness':
            # Automatic brightness adjustment
            lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
            l = clahe.apply(l)
            enhanced = cv2.merge([l, a, b])
            return cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)

        elif mode == 'contrast':
            # Increase contrast
            alpha = 1.5  # Contrast control
            beta = 0     # Brightness control
            return cv2.convertScaleAbs(frame, alpha=alpha, beta=beta)

        elif mode == 'adaptive':
            # Adaptive histogram equalization
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(gray)
            return cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)

        return frame

    def draw_overlay(self, frame, metrics, mode):
        """Draw informative overlay on frame"""
        overlay = frame.copy()
        h, w = frame.shape[:2]

        # Create info panel background
        cv2.rectangle(overlay, (10, 10), (350, 200), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

        # Draw text information
        y_offset = 35
        cv2.putText(frame, "CAMERA LIGHTING TEST", (20, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        y_offset += 30
        cv2.putText(frame, f"Condition: {metrics['condition']}", (20, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, metrics['color'], 2)

        y_offset += 25
        cv2.putText(frame, f"Brightness: {metrics['mean']:.1f} (0-255)", (20, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        y_offset += 25
        cv2.putText(frame, f"Contrast: {metrics['std']:.1f} ({metrics['contrast_level']})", (20, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        y_offset += 25
        cv2.putText(frame, f"Range: {metrics['min']}-{metrics['max']}", (20, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        y_offset += 25
        cv2.putText(frame, f"Mode: {mode.upper()}", (20, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 200, 255), 1)

        # Draw histogram
        hist_h = 100
        hist_w = 256
        hist_img = np.zeros((hist_h, hist_w, 3), dtype=np.uint8)
        hist = metrics['histogram']
        hist = hist / hist.max() * hist_h

        for i in range(256):
            cv2.line(hist_img, (i, hist_h), (i, hist_h - int(hist[i])), (255, 255, 255), 1)

        # Place histogram at bottom right
        frame[h-hist_h-10:h-10, w-hist_w-10:w-10] = hist_img

        # Draw brightness bar
        brightness_pct = metrics['mean'] / 255.0
        bar_w = 300
        bar_h = 20
        bar_x, bar_y = 20, h - 40

        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (50, 50, 50), -1)
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + int(bar_w * brightness_pct), bar_y + bar_h),
                     metrics['color'], -1)
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (255, 255, 255), 2)

        return frame

    def print_instructions(self):
        """Print usage instructions"""
        print("\n" + "="*60)
        print("CAMERA LIGHTING TEST - CONTROLS")
        print("="*60)
        print("  Q or ESC : Quit")
        print("  S        : Save current frame")
        print("  0        : No enhancement")
        print("  1        : Brightness adjustment (CLAHE)")
        print("  2        : Contrast enhancement")
        print("  3        : Adaptive equalization")
        print("  SPACE    : Print current metrics")
        print("="*60 + "\n")

    def run(self):
        """Main test loop"""
        if not self.initialize_camera():
            return

        self.print_instructions()

        enhancement_mode = 'none'
        frame_count = 0

        print("[INFO] Press Q or ESC to quit")
        print("[INFO] Showing camera feed...\n")

        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("[ERROR] Failed to grab frame")
                break

            frame_count += 1

            # Analyze lighting
            metrics = self.analyze_lighting(frame)

            # Apply enhancement if selected
            enhanced_frame = self.apply_enhancements(frame, enhancement_mode)

            # Draw overlay with metrics
            display_frame = self.draw_overlay(enhanced_frame, metrics, enhancement_mode)

            # Show frame
            cv2.imshow('Camera Lighting Test', display_frame)

            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF

            if key == ord('q') or key == 27:  # Q or ESC
                print("\n[INFO] Quitting...")
                break

            elif key == ord('s'):  # Save frame
                filename = f"camera_test_frame_{frame_count}.jpg"
                cv2.imwrite(filename, frame)
                print(f"[INFO] Frame saved as {filename}")

            elif key == ord('0'):
                enhancement_mode = 'none'
                print("[INFO] Enhancement: None")

            elif key == ord('1'):
                enhancement_mode = 'brightness'
                print("[INFO] Enhancement: Brightness (CLAHE)")

            elif key == ord('2'):
                enhancement_mode = 'contrast'
                print("[INFO] Enhancement: Contrast")

            elif key == ord('3'):
                enhancement_mode = 'adaptive'
                print("[INFO] Enhancement: Adaptive")

            elif key == ord(' '):  # Space - print metrics
                print(f"\n--- Frame {frame_count} Metrics ---")
                print(f"Condition: {metrics['condition']}")
                print(f"Mean Brightness: {metrics['mean']:.2f}")
                print(f"Contrast (Std Dev): {metrics['std']:.2f} ({metrics['contrast_level']})")
                print(f"Range: {metrics['min']} - {metrics['max']}")
                print(f"Enhancement Mode: {enhancement_mode}")
                print("-" * 35 + "\n")

        self.cleanup()

    def cleanup(self):
        """Release resources"""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        print("[INFO] Camera released")

if __name__ == "__main__":
    print("="*60)
    print("  CAMERA LIGHTING CONDITION TEST")
    print("="*60)

    # Allow camera ID as command line argument
    camera_id = 0
    if len(sys.argv) > 1:
        camera_id = int(sys.argv[1])

    tester = CameraLightingTest(camera_id)
    tester.run()
