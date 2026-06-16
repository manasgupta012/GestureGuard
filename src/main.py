import os
import cv2
import time
from datetime import datetime
from dotenv import load_dotenv
from pushbullet import Pushbullet
from gesture_detector import GestureDetector 

# Load hidden secrets from .env file
load_dotenv()
API_KEY = os.getenv("PUSHBULLET_API_KEY") 

def send_phone_notification(timestamp):
    """Sends a push notification directly to your smartphone via Pushbullet."""
    try:
        if not API_KEY:
            print("⚠️ Notification skipped: No API Key found in .env file!")
            return
            
        pb = Pushbullet(API_KEY)
        title = "🚨 EMERGENCY: GestureGuard Alert!"
        body = f"An SOS gesture was detected and verified at {timestamp}. Please check the monitor."
        
        pb.push_note(title, body)
        print("📱 PUSH NOTIFICATION SENT SUCCESSFULLY TO YOUR PHONE!")
    except Exception as e:
        print(f"❌ Failed to send phone notification: {e}")

def log_alert():
    """Creates an 'alerts' folder if it doesn't exist and logs the incident."""
    folder_path = "alerts"
    file_path = os.path.join(folder_path, "alerts.log")
    
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print("📁 Created a brand-new 'alerts' folder!")

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[ALERT] SOS Gesture Detected at: {current_time}\n"
    
    with open(file_path, "a") as log_file:
        log_file.write(log_line)
    
    print(f"✨ NEW LOG WRITTEN successfully to: {file_path} at {current_time}")
    send_phone_notification(current_time)

def main():
    cap = cv2.VideoCapture(0)
    detector = GestureDetector()

    # --- Cooldown Configuration ---
    last_alert_time = 0        # Timestamp of the last triggered alert
    COOLDOWN_PERIOD = 7.0      # System locks for 7 seconds after an alert

    print("GestureGuard Running... Press 'q' to quit.")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        frame = cv2.flip(frame, 1)
        current_time = time.time()

        # 1. Check if we are allowed to process detection or if we are in cooldown
        if current_time - last_alert_time > COOLDOWN_PERIOD:
            is_sos_triggered = detector.detect(frame)
            if is_sos_triggered:
                print("🚨 SOS ALERT TRIGGERED! 🚨")
                log_alert()  
                last_alert_time = current_time  # Start the cooldown timer
        else:
            # Display a prominent red warning banner across the screen during cooldown
            time_left = int(COOLDOWN_PERIOD - (current_time - last_alert_time))
            cv2.putText(
                frame, 
                f"SYSTEM LOCKED (COOLDOWN): {time_left}s", 
                (30, 45), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                0.7, 
                (0, 0, 255), 
                2
            )

        # 2. Draw the standard UI overlays (Yellow Box / Green Hand Box)
        frame = detector.draw_roi(frame)

        # 3. Display the live execution window
        cv2.imshow("GestureGuard - SOS Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()