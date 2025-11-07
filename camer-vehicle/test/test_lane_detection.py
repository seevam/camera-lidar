"""Test lane detection with sample images"""

import cv2
import sys
sys.path.append('../src')
from lane_detector import LaneDetector

# Test configuration
config = {
    'threshold': 60,
    'roi_top_percent': 0.6,
    'min_contour_area': 500
}

def test_single_image():
    detector = LaneDetector(config)
    
    # Load test image
    img = cv2.imread('test_images/straight_line.jpg')
    
    # Detect lane
    position, confidence, processed = detector.detect(img)
    
    print(f"Position: {position}, Confidence: {confidence:.2f}")
    
    # Show results
    cv2.imshow('Original', img)
    cv2.imshow('Processed', processed)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def test_video():
    detector = LaneDetector(config)
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        position, confidence, processed = detector.detect(frame)
        
        # Draw position
        cv2.line(processed, (position, 0), (position, 480), (0, 255, 0), 2)
        
        cv2.imshow('Lane Detection', processed)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    print("1. Testing with image...")
    test_single_image()
    
    print("\n2. Testing with video...")
    test_video()
