import os
import cv2
import time
from datetime import datetime
from dotenv import load_dotenv     # New import
from pushbullet import Pushbullet
from gesture_detector import GestureDetector 

# Load the hidden .env file
load_dotenv()

# Securely grab the key from your environment
API_KEY = os.getenv("PUSHBULLET_API_KEY") 

def send_phone_notification(timestamp):
    # ... (rest of your send_phone_notification function stays exactly the same)