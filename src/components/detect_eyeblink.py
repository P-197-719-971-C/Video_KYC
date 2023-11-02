import cv2 as cv
import time
import math
import numpy as np
import mediapipe as mp
from src.utils.utility import euclidean_distance, point, LivePlot, GREEN, MAGENTA
from src.logger.logger import logging
from scipy.signal import argrelextrema
import scipy.signal


def calculate_eye_aspect_ratio(face, img):
    logging.info("Calculating eye aspect ratio")
    # right eye
    rightUp = face[159]
    rightDown = face[23]
    rightLeft = face[130]
    rightRight = face[243]
    lenghtVer_right = euclidean_distance(rightUp, rightDown)
    lenghtHor_right= euclidean_distance(rightLeft, rightRight)
    cv.line(img, point(rightUp, img), point(rightDown, img), GREEN, 3)
    cv.line(img, point(rightLeft, img), point(rightRight, img), GREEN, 3)
    ratio_right = int((lenghtVer_right / lenghtHor_right) * 100)
    
    # left eye
    leftUp = face[386]
    leftDown = face[374]
    leftLeft = face[382]
    leftRight = face[263]
    lenghtVer_left = euclidean_distance(leftUp, leftDown)
    lenghtHor_left = euclidean_distance(leftLeft, leftRight)
    cv.line(img, point(leftUp, img), point(leftDown, img), GREEN, 3)
    cv.line(img, point(leftLeft, img), point(leftRight, img), GREEN, 3)
    ratio_left = int((lenghtVer_left / lenghtHor_left) * 100)
    
    ratio = (ratio_right+ratio_left)/2
    return ratio

def facial_htw_ratio(face, img):
    #Calculating ratio of vertical length and horizontal length of face
    logging.info("Calculating the intersection point of face height and width")
    faceUp = face[10]
    faceDown = face[152]
    faceLeft = face[323]
    faceRight = face[93]
    face_vert = euclidean_distance(faceUp, faceDown)
    face_hor = euclidean_distance(faceLeft, faceRight)
    cv.line(img, point(faceUp, img), point(faceDown, img),  GREEN, 3)
    cv.line(img, point(faceLeft, img), point(faceRight, img),  GREEN, 3)

    ratio_face = int(face_vert/ (2 * face_hor) * 100)
    angle_vert = math.atan2(faceDown.y - faceUp.y, faceDown.x - faceUp.x)
    angle_hor = math.atan2(faceRight.y - faceLeft.y, faceRight.x - faceLeft.x)
    slope_vert = math.tan(angle_vert)
    slope_hor = math.tan(angle_hor)
    intercept_vert = faceUp.y - slope_vert * faceUp.x
    intercept_hor = faceLeft.y - slope_hor * faceLeft.x
    intersection_x = (intercept_vert - intercept_hor) / (slope_hor - slope_vert)
    intersection_y = slope_vert * intersection_x + intercept_vert
    intersection_point = (int(intersection_x), int(intersection_y))
    return intersection_y, ratio_face



def detect_eye_blink(cap , smoothing_frames:int = 3, order: int = 20):
    start_time = time.time()
    logging.info("Detecting eye blink function instantiated")
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)
    plotY = LivePlot(640, 360, [20, 80], invert=True)
    idList = [0, 22, 23, 24, 26, 110, 157, 158, 159, 160, 161, 130, 243, 362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385,384, 398, 10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103,67, 109]
    # left eye = [22, 23, 24, 26, 110, 157, 158, 159, 160, 161, 130, 243]
    # right eye = [ 33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161 , 246 ]
    # FACE_OVAL=[ 10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103,67, 109]

    ratioList = []
    ratioAvgList = []
    blinkCounter = 0
    counter = 0
    color = MAGENTA

    logging.info("Checking if video is opened")
    while cap.isOpened():
        isTrue, img = cap.read()
        if not isTrue:
            logging.info("Frame not Found")
            break

        results = face_mesh.process(img)
        logging.info("Getting facial landmarks")
        if results.multi_face_landmarks:
            for face_landmark in results.multi_face_landmarks:
                face = [face_landmark.landmark[i] for i in range(468)]
            logging.info("getting image shape")
            logging.info("iterating through face indexes")
            for id in idList:
                logging.info("Putting index as text for each landmark")
                cv.putText(img = img, text = str(id), org=point(face[id], img), fontScale=0.2, fontFace= cv.FONT_HERSHEY_COMPLEX, color=color)
        
            ratio = calculate_eye_aspect_ratio(face, img)
            intersection_y, ratio_face = facial_htw_ratio(face, img)
            
            if intersection_y < face[0].y:
                ratioList.append(ratio)
                if len(ratioList) > smoothing_frames:
                    ratioList.pop(0)
                ratioAvg = round(sum(ratioList) / len(ratioList), 1)
                ratioAvgList.append(ratioAvg)
                
            imgPlot = plotY.update(ratioAvg, color)
            img = cv.resize(img, (640, 360))
            cv.putText(img= img, text= f'Eye aspect ratio: {ratio}\n Face ratio: {ratio_face}', org = (10, 30),fontFace= cv.FONT_HERSHEY_COMPLEX, fontScale= 0.5, color = color, thickness= 2)
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
    

# Frame Processing Code

    end_time = time.time()
    total_time = end_time - start_time
    
    average_frame_time = total_time / total_frames
    print(total_time)
    print(average_frame_time)
    return average
