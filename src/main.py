import cv2
import time

from gesture_detector import GestureDetector
from notifier import send_alert

detector = GestureDetector()

cap = cv2.VideoCapture(0)

# Alert cooldown tracking variables
alert_cooldown = 10
last_alert_time = 0

while True:

    ret, frame = cap.read()

    if not ret:
        break

    frame = cv2.flip(frame, 1)

    # 1. Draw the ROI overlay zone on the screen
    frame = detector.draw_roi(frame)

    # 2. Check if the updated detector registers a completed double-wave gesture
    # FIXED: Re-added the exact assignment variable name 'detections' so it aligns with your architecture
    detections = detector.detect(frame) 

    current_time = time.time()

    # 3. Handle Alert Triggering
    if detections: # FIXED: Swapped 'double_wave_detected' to match 'detections'
        # Check if we are outside the 10-second alert cooldown period
        if current_time - last_alert_time > alert_cooldown:
            print("SOS ALERT TRIGGERED")
            send_alert()
            last_alert_time = current_time
            
            # Draw a temporary visual confirmation on screen
            cv2.putText(
                frame,
                "ALERT SENT!",
                (20, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),  # Red color for alert
                3
            )
        else:
            print("Alert triggered, but blocked by cooldown period.")

    cv2.imshow("GestureGuard", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()