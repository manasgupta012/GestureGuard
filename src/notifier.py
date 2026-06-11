from plyer import notification

def send_alert():

    notification.notify(
        title="GestureGuard",
        message="Detection Triggered",
        timeout=3
    )