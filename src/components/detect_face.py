import sys
from pathlib import Path
from src.logger.logger import logging
from src.exception.exception import CustomException
import cv2

faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades+'haarcascade_frontalface_default.xml')
video_capture = cv2.VideoCapture("capture.avi")
if not video_capture.isOpened():
    print("Error: Could not open video file.")
    sys.exit()
while True:
    ret, frame = video_capture.read()
    if not ret:
        break
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(gray, 1.3, 5)
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (95, 207, 30), 3)
        cv2.rectangle(frame, (x, y - 40), (x + w, y), (95, 207, 30), -1)
        cv2.putText(frame, "Face", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)

    cv2.imshow('Video', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
video_capture.release()
cv2.destroyAllWindows()