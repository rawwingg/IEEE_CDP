import numpy as np
import cv2
from picamera2 import Picamera2

#Ball and target color detection

picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"format": "BGR888", "size": (1280, 720)})
picam2.configure(config)
picam2.start()

kernal = np.ones((5, 5), "uint8")

while True:
    imageFrame = picam2.capture_array()
    imageFrame = cv2.cvtColor(imageFrame, cv2.COLOR_RGB2BGR)
    hsvFrame = cv2.cvtColor(imageFrame, cv2.COLOR_BGR2HSV)

    # Red
    red_lower = np.array([167, 125, 169], np.uint8)
    red_upper = np.array([179, 200, 221], np.uint8)
    red_mask = cv2.dilate(cv2.inRange(hsvFrame, red_lower, red_upper), kernal)

    # Green
    green_lower = np.array([56, 90, 101], np.uint8)
    green_upper = np.array([80, 205, 154], np.uint8)
    green_mask = cv2.dilate(cv2.inRange(hsvFrame, green_lower, green_upper), kernal)

    # Blue
    blue_lower = np.array([101, 197, 151], np.uint8)
    blue_upper = np.array([108, 255, 210], np.uint8)
    blue_mask = cv2.dilate(cv2.inRange(hsvFrame, blue_lower, blue_upper), kernal)

    # Tennis ball
    tennis_lower = np.array([25, 80, 80], np.uint8)
    tennis_upper = np.array([45, 255, 255], np.uint8)
    tennis_mask = cv2.dilate(cv2.inRange(hsvFrame, tennis_lower, tennis_upper), kernal)

    # Track red
    contours, _ = cv2.findContours(red_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        if cv2.contourArea(contour) > 300:
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(imageFrame, (x, y), (x+w, y+h), (0, 0, 255), 2)
            cv2.putText(imageFrame, "Red", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

    # Track green
    contours, _ = cv2.findContours(green_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        if cv2.contourArea(contour) > 300:
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(imageFrame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(imageFrame, "Green", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    # Track blue
    contours, _ = cv2.findContours(blue_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        if cv2.contourArea(contour) > 300:
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(imageFrame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            cv2.putText(imageFrame, "Blue", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

    # Track tennis ball — with circularity filter
    contours, _ = cv2.findContours(tennis_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for contour in sorted(contours, key=cv2.contourArea, reverse=True):
        area = cv2.contourArea(contour)
        if area < 1300:
            continue

        # Circularity check — rejects non-round shapes
        perimeter = cv2.arcLength(contour, True)
        if perimeter == 0:
            continue
        circularity = (4 * np.pi * area) / (perimeter ** 2)
        if circularity < 0.75:
            continue

        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(imageFrame, (x, y), (x+w, y+h), (0, 255, 255), 2)
        cv2.putText(imageFrame, f"Tennis ({circularity:.2f})", (x, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)

    cv2.imshow("Color Detection", imageFrame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

picam2.stop()
cv2.destroyAllWindows()