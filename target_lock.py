import numpy as np
import cv2
from picamera2 import Picamera2
import lgpio
import time

# Servo GPIO pins
s2 = 13

PWM_FREQ = 50
CENTER_TOLERANCE = 30
TURN_ANGLE = 5
MIN_AREA = 500

# Start servo angle
servo_angle = 90

# Open GPIO chip
h2 = lgpio.gpiochip_open(0)

lgpio.gpio_claim_output(h2, s2)

def set_servo_angle(angle, SERVO_GPIO, h):
    angle = max(0, min(180, angle))
    pulse_us = int(500 + (angle / 180.0) * 2000)
    lgpio.tx_servo(h, SERVO_GPIO, pulse_us, PWM_FREQ)
    print(f"Servo GPIO {SERVO_GPIO}: {angle} deg")
    return angle

def stop():
    print("Target centered")

try:
    # Initial servo positions
    set_servo_angle(0, s1, h1)
    servo_angle = set_servo_angle(servo_angle, s2, h2)
    time.sleep(1)

    # Camera setup
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(
        main={"format": "BGR888", "size": (1280, 720)}
    )
    picam2.configure(config)
    picam2.start()
    time.sleep(1)

    kernel = np.ones((5, 5), np.uint8)

    while True:
        imageFrame = picam2.capture_array()

        height, width, _ = imageFrame.shape
        frame_center_x = width // 2

        hsvFrame = cv2.cvtColor(imageFrame, cv2.COLOR_BGR2HSV)

        # Red range 1
        red_lower1 = np.array([0, 120, 70], np.uint8)
        red_upper1 = np.array([10, 255, 255], np.uint8)

        # Red range 2
        red_lower2 = np.array([167, 125, 169], np.uint8)
        red_upper2 = np.array([179, 255, 255], np.uint8)

        red_mask1 = cv2.inRange(hsvFrame, red_lower1, red_upper1)
        red_mask2 = cv2.inRange(hsvFrame, red_lower2, red_upper2)
        red_mask = red_mask1 + red_mask2

        red_mask = cv2.erode(red_mask, kernel)
        red_mask = cv2.dilate(red_mask, kernel)

        contours, _ = cv2.findContours(
            red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        found_target = False

        if contours:
            largest = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest)

            if area > MIN_AREA:
                found_target = True

                x, y, w, h = cv2.boundingRect(largest)
                target_center_x = x + w // 2

                error = target_center_x - frame_center_x

                cv2.rectangle(imageFrame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.circle(imageFrame, (target_center_x, y + h // 2), 5, (0, 255, 0), -1)
                cv2.line(
                    imageFrame,
                    (frame_center_x, 0),
                    (frame_center_x, height),
                    (255, 0, 0),
                    2,
                )

                cv2.putText(
                    imageFrame,
                    "Red Target",
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                    (0, 0, 255),
                    2,
                )

                if abs(error) <= CENTER_TOLERANCE:
                    stop()

                elif error < 0:
                    # Target is left of center
                    servo_angle -= TURN_ANGLE
                    servo_angle = set_servo_angle(servo_angle, s2, h2)
                    time.sleep(0.1)

                else:
                    # Target is right of center
                    servo_angle += TURN_ANGLE
                    servo_angle = set_servo_angle(servo_angle, s2, h2)
                    time.sleep(0.1)

        if not found_target:
            # Red not found, scan side to side
            servo_angle += TURN_ANGLE

            if servo_angle > 180:
                servo_angle = 0

            servo_angle = set_servo_angle(servo_angle, s2, h2)
            time.sleep(0.1)

        cv2.imshow("Color Detection", imageFrame)
        cv2.imshow("Red Mask", red_mask)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

except KeyboardInterrupt:
    print("Stopped by user")

finally:
    picam2.stop()
    cv2.destroyAllWindows()

    lgpio.tx_servo(h2, s2, 0, PWM_FREQ)

    lgpio.gpiochip_close(h1)
    lgpio.gpiochip_close(h2)