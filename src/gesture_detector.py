import cv2
import time
import os
import urllib.request  # Built-in library to handle the automatic download
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

class GestureDetector:

    def __init__(self):
        # SOS Zone (x, y, width, height)
        self.roi = (200, 100, 250, 250)
        
        # --- Modern MediaPipe Tasks Setup ---
        model_path = os.path.abspath("hand_landmarker.task")
        
        # 5% POLISH LAYER: Automatic fail-safe download if the file is deleted or missing
        if not os.path.exists(model_path):
            print("\n🚨 Model asset missing! Auto-downloading 'hand_landmarker.task' from Google...")
            url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
            try:
                urllib.request.urlretrieve(url, model_path)
                print("✅ Download complete! Initializing AI tracking engine...\n")
            except Exception as e:
                raise RuntimeError(f"Failed to auto-download model from Google. Error: {e}")
            
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.HandLandmarkerOptions(base_options=base_options, num_hands=1)
        self.detector = vision.HandLandmarker.create_from_options(options)
        
        # --- Gesture Tracking Variables ---
        self.hand_state = "UNKNOWN"   # Tracks "OPEN", "FIST", or "UNKNOWN"
        self.fist_counter = 0         # Counts complete fist-pump cycles
        self.last_state_time = 0
        self.TIME_WINDOW = 3.0        # Max seconds allowed to complete the gesture

    def detect(self, frame):
        x, y, w, h = self.roi
        roi_frame = frame[y:y+h, x:x+w]
        
        # Convert the frame to RGB and wrap it inside a MediaPipe Image object
        rgb_roi = cv2.cvtColor(roi_frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_roi)
        
        # Process detection
        results = self.detector.detect(mp_image)
        
        current_time = time.time()
        
        # Reset gesture progression if the user takes too long between actions
        if self.fist_counter > 0 and (current_time - self.last_state_time) > self.TIME_WINDOW:
            self.fist_counter = 0
            self.hand_state = "UNKNOWN"
            print("Gesture window expired. Resetting counter.")

        if results.hand_landmarks:
            # Focus on the primary detected hand inside the ROI
            hand_landmarks = results.hand_landmarks[0]
            
            # MediaPipe skeletal joint indices in modern Tasks API:
            # Tips: Index (8), Middle (12), Ring (16), Pinky (20)
            # Knuckles (PIP joints): Index (6), Middle (10), Ring (14), Pinky (18)
            finger_tips = [8, 12, 16, 20]
            finger_knuckles = [6, 10, 14, 18]
            
            # Count how many fingers are extended straight up
            extended_fingers = 0
            for tip, knuckle in zip(finger_tips, finger_knuckles):
                # If a finger tip Y coordinate is less than its knuckle Y, the finger is open.
                if hand_landmarks[tip].y < hand_landmarks[knuckle].y:
                    extended_fingers += 1
                    
            # Set the immediate state of the hand based on skeleton data
            if extended_fingers >= 4:
                current_state = "OPEN"
            elif extended_fingers == 0:
                current_state = "FIST"
            else:
                current_state = "UNKNOWN"

            # --- Gesture Logic State Machine ---
            if current_state == "FIST" and self.hand_state == "OPEN":
                # Success: User closed an open hand into a fist deliberate pump
                self.fist_counter += 1
                self.hand_state = "FIST"
                self.last_state_time = current_time
                print(f"Fist pump registered! Count: {self.fist_counter}")
                
                if self.fist_counter >= 2:
                    self.fist_counter = 0  # Reset parameters
                    self.hand_state = "UNKNOWN"
                    return True  # ALERT TRIGGERED! 2 FIST PUMPS COMPLETED

            elif current_state == "OPEN":
                # Ready the system for the next fist clench
                self.hand_state = "OPEN"

        return False

    def draw_roi(self, frame):
        x, y, w, h = self.roi
        # Draw the target box
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)
        
        # Display live feedback tracking on the main screen
        status_text = f"SOS ZONE | Fists: {self.fist_counter} | State: {self.hand_state}"
        cv2.putText(
            frame,
            status_text,
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 255),
            2
        )
        return frame