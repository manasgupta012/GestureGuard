import cv2
import numpy as np
import time

class GestureDetector:

    def __init__(self):
        # SOS Zone (x, y, width, height)
        self.roi = (200, 100, 250, 250)
        
        # --- Gesture Logic Tracking Variables ---
        self.wave_counter = 0
        self.last_direction = None
        self.last_cx = None
        self.wave_timestamp = 0
        
        # Thresholds tailored for hand waving
        self.MOVEMENT_THRESHOLD = 20  # Minimum horizontal shift in pixels
        self.TIME_WINDOW = 2.0        # Max seconds allowed between wave cycles
        self.MIN_HAND_AREA = 2000     # Drop noise, focus on actual hand size

    def detect(self, frame):
        x, y, w, h = self.roi
        roi_frame = frame[y:y+h, x:x+w]

        # 1. Convert ROI to HSV color space (Much better for lighting changes than RGB)
        hsv = cv2.cvtColor(roi_frame, cv2.COLOR_BGR2HSV)

        # 2. Define Skin Color Boundaries in HSV space
        # These bounds target human skin across various ethnicities and lighting conditions
        lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        upper_skin = np.array([20, 255, 255], dtype=np.uint8)

        # 3. Create a binary mask (isolates ONLY skin pixels)
        mask = cv2.inRange(hsv, lower_skin, upper_skin)

        # 4. Apply Blurring and Morphology to eliminate speckles/noise
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask = cv2.dilate(mask, kernel, iterations=2)
        mask = cv2.GaussianBlur(mask, (5, 5), 0)

        # Optional: Uncomment the next line to visually see what your detector isolates as "skin"
        # cv2.imshow("Skin Detection Mask", mask)

        # 5. Find contours of the isolated skin regions
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        current_time = time.time()
        
        # Reset tracking data if the time window between waves expires
        if self.wave_counter > 0 and (current_time - self.wave_timestamp) > self.TIME_WINDOW:
            self.wave_counter = 0
            self.last_direction = None

        largest_contour = None
        max_area = 0

        # Find the single largest skin-colored blob (the hand) inside the SOS Zone
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > self.MIN_HAND_AREA and area > max_area:
                max_area = area
                largest_contour = contour

        # If an actual hand is present and moving
        if largest_contour is not None:
            bx, by, bw, bh = cv2.boundingRect(largest_contour)
            
            # Find the horizontal center (cx) of the hand
            cx = bx + (bw // 2)

            if self.last_cx is None:
                self.last_cx = cx
                return False

            # Check horizontal distance change between frames
            movement = cx - self.last_cx

            if abs(movement) > self.MOVEMENT_THRESHOLD:
                current_direction = "Right" if movement > 0 else "Left"

                # Check for a sharp direction flip (Left to Right / Right to Left)
                if self.last_direction is not None and current_direction != self.last_direction:
                    self.wave_counter += 1
                    self.wave_timestamp = current_time
                    
                    if self.wave_counter >= 2:
                        self.wave_counter = 0  # Reset parameters after triggering alert
                        self.last_direction = None
                        self.last_cx = cx
                        return True  # 2 WAVES REGISTERED!

                self.last_direction = current_direction
                self.last_cx = cx

        return False

    def draw_roi(self, frame):
        x, y, w, h = self.roi
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)
        cv2.putText(
            frame,
            f"SOS ZONE | Waves: {self.wave_counter}",
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 255),
            2
        )
        return frame