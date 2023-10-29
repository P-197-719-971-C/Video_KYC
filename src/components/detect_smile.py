import cv2 as cv
import time
import math
import numpy as np
import mediapipe as mp
from src.components.utility import euclidean_distance, point, LivePlot, GREEN, MAGENTA
from src.logger.logger import logging
from scipy.signal import argrelextrema
import scipy.signal
from src.components.detect_eyeblink import detect_eye_blink

def smile_ratio(face, img):
    noseDown = face[2]
    lipupUp = face[0]
    lipupDown = face[13]
    lipdownUp = face[14]
    lipdownDown = face[17]
    lipLeft = face[291]
    lipRight = face[61]
    chickRight = face[205]
    chickLeft = face[425]

    # Metric 1
    noseTolipup = euclidean_distance(noseDown, lipupUp)
    lipVet = euclidean_distance(lipupUp, lipdownDown)
    cv.line(img, point(noseDown, img), point(lipupUp, img), (0,0,255), 3)
    cv.line(img, point(lipupUp, img), point(lipdownDown, img), (0, 200, 0), 3)
    ratio1 = noseTolipup/ lipVet * 100
    # Metric 2
    lipHor= euclidean_distance(lipLeft, lipRight)
    lipToChickRight= euclidean_distance(lipRight, chickRight)
    lipToChickLeft = euclidean_distance(lipLeft, chickLeft)

    cv.line(img, point(lipLeft, img), point(lipRight, img),(0, 200, 0), 3)
    cv.line(img, point(lipRight, img), point(chickRight, img), (0,0,255), 3)
    cv.line(img, point(lipLeft, img), point(chickLeft, img), (0,0,255), 3)
    
    ratio2 = (lipToChickLeft + lipToChickRight)/lipHor * 100

    ratio = int(0.6 * ratio1 + 0.4 * ratio2)
    return ratio
def detect_smile(cap, smoothing_frames:int = 3, order:int = 20):
    start_time = time.time()
    logging.info("Detecting eye blink function instantiated")
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)
    plotY = LivePlot(640, 360, [20, 150], invert=True)
    idList = [1, 2, 98, 327, 205, 425, 164, 61, 146, 91, 181, 84, 17, 314, 405, 321, 375,291, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95,185, 40, 39, 37,0 ,267 ,269 ,270 ,409, 415, 310, 311, 312, 13, 82, 81, 42, 183, 78,  10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103,67, 109]
    # below_nose_point = 164
    # midwayBetweenEyes: [168],

    # noseTip: [1]
    # noseBottom: [2],
    # noseRightCorner: [98],
    # noseLeftCorner: [327],

    # rightCheek: [205],
    # leftCheek: [425]
    # LOWER_LIPS =[61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95]
    # UPPER_LIPS=[ 185, 40, 39, 37,0 ,267 ,269 ,270 ,409, 415, 310, 311, 312, 13, 82, 81, 42, 183, 78] 
    # FACE_OVAL=[ 10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103,67, 109]
    ratioList = []
    ratioAvgList = []
    color = MAGENTA

    while True:
        isTrue, img = cap.read()
        if not isTrue:
            break
        results = face_mesh.process(img)
        if results.multi_face_landmarks:
            for face_landmark in results.multi_face_landmarks:
                face = [face_landmark.landmark[i] for i in range(468)]
            
            for id in idList:
                logging.info("Putting index as text for each landmark")
                cv.putText(img = img, text = str(id), org=point(face[id], img), fontScale=0.1, fontFace= cv.FONT_HERSHEY_COMPLEX, color=color)
                
            ratio = smile_ratio(face, img)
            
            ratioList.append(ratio)
            if len(ratioList) > smoothing_frames:
                ratioList.pop(0)
            ratioAvg = round(sum(ratioList) / len(ratioList), 1)
            ratioAvgList.append(ratioAvg)

            imgPlot = plotY.update(ratioAvg, color)
            img = cv.resize(img, (640, 360))
            cv.putText(img= img, text= f'smile ratio: {ratio}', org = (10, 30),fontFace= cv.FONT_HERSHEY_COMPLEX, fontScale= 0.5, color = color, thickness= 2)
            stacked_img = np.hstack((img, imgPlot))
            cv.imshow("Image", stacked_img)
        else:
            img = cv.resize(img, (640, 360))
            cv.imshow("Image", img)

        key = cv.waitKey(1)
        if key==ord('q') or key ==ord('Q'):
            break
    local_minima_indices = argrelextrema(np.array(ratioAvgList), np.less, order= order)[0]
    local_minima_values = [ratioAvgList[i] for i in local_minima_indices]
    print(local_minima_values)
    average = sum(local_minima_values)/len(local_minima_values)
    print(len(local_minima_values))
    print(average)
    video_duration_minutes = cap.get(cv.CAP_PROP_FRAME_COUNT) / cap.get(cv.CAP_PROP_FPS) / 60
    print(f"video duration: {video_duration_minutes}")
    total_frames = cap.get(cv.CAP_PROP_FRAME_COUNT)
    cap.release()
    cv.destroyAllWindows()
    end_time = time.time()
    total_time = end_time - start_time
    
    average_frame_time = total_time / (total_frames+0.001)
    print(total_time)
    print(average_frame_time)
    return average
    


if __name__ == "__main__":
    cap = cv.VideoCapture("capture.avi")
    # Measure the start time
    detect_eye_blink(cap)
    detect_smile(cap)
    