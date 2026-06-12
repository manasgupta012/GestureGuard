import cv2
import numpy as np
import time

class GestureDetector:

    def __init__(self):
        self.roi = (200, 100, 250, 250)

        self.wave_counter = 0
        self.last_direction = None
        self.last_cx = None
        self.wave_timestamp = 0

        self.MOVEMENT_THRESHOLD = 20
        self.TIME_WINDOW = 2.0
        self.MIN_HAND_AREA = 2000

    def detect(self, frame):

        x, y, w, h = self.roi
        roi_frame = frame[y:y+h, x:x+w]

        hsv = cv2.cvtColor(roi_frame, cv2.COLOR_BGR2HSV)

        lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        upper_skin = np.array([20, 255, 255], dtype=np.uint8)

        mask = cv2.inRange(hsv, lower_skin, upper_skin)

        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask = cv2.dilate(mask, kernel, iterations=2)
        mask = cv2.GaussianBlur(mask, (5, 5), 0)

        contours, _ = cv2.findContours(
            mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        current_time = time.time()

        if self.wave_counter > 0 and (current_time - self.wave_timestamp) > self.TIME_WINDOW:
            self.wave_counter = 0
            self.last_direction = None

        largest_contour = None
        max_area = 0

        for contour in contours:

            area = cv2.contourArea(contour)

            if area > self.MIN_HAND_AREA and area > max_area:

                max_area = area
                largest_contour = contour
                self.current_bbox = cv2.boundingRect(contour)

        if largest_contour is not None:

            bx, by, bw, bh = cv2.boundingRect(largest_contour)

            cx = bx + (bw // 2)

            if self.last_cx is None:
                self.last_cx = cx
                return False

            movement = cx - self.last_cx

            if abs(movement) > self.MOVEMENT_THRESHOLD:

                current_direction = "Right" if movement > 0 else "Left"

                if self.last_direction is not None and current_direction != self.last_direction:

                    self.wave_counter += 1
                    self.wave_timestamp = current_time

                    if self.wave_counter >= 2:

                        self.wave_counter = 0
                        self.last_direction = None
                        self.last_cx = cx

                        return True

                self.last_direction = current_direction
                self.last_cx = cx

        return False

    def draw_roi(self, frame):

        x, y, w, h = self.roi

        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            (0, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f"SOS ZONE | Waves: {self.wave_counter}",
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 255),
            2
        )

        if hasattr(self, "current_bbox"):

            bx, by, bw, bh = self.current_bbox

            cv2.rectangle(
                frame,
                (x + bx, y + by),
                (x + bx + bw, y + bh),
                (0, 255, 0),
                2
            )

        return frame