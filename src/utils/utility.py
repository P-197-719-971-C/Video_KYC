import cv2 as cv 
import numpy as np
import math
import time
from src.logger.logger import logging
from collections import deque

# colors 
# values =(blue, green, red) opencv accepts BGR values not RGB
BLACK = (0,0,0)
WHITE = (255,255,255)
BLUE = (255,0,0)
RED = (0,0,255)
CYAN = (255,255,0)
YELLOW =(0,255,255)
MAGENTA = (255,0,255)
GRAY = (128,128,128)
GREEN = (0,255,0)
PURPLE = (128,0,128)
ORANGE = (0,165,255)
PINK = (147,20,255)

def euclidean_distance(point1, point2):
    logging.info(f"calculating euclidean distance between {point1} and {point1}")
    return math.sqrt((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2 )
def point(ladmark_with_index, img):
    logging.info(f"Converting normalized point {ladmark_with_index} to original")
    height, width, _ = img.shape
    pt = (int(ladmark_with_index.x * width), int(ladmark_with_index.y * height))
    return pt

class LivePlot:
    """
    A class for real-time plotting in OpenCV.
    """

    def __init__(self, w=640, h=480, yLimit=[0, 100], interval=0.001, invert=True, char='Y'):
        """
        Initialize the LivePlot object.

        :param w: Width of the plotting window
        :param h: Height of the plotting window
        :param yLimit: Y-axis limits [y_min, y_max]
        :param interval: Time interval for updating the plot
        :param invert: Whether to invert the y-axis
        :param char: A character to display on the plot for annotation
        """

        self.yLimit = yLimit
        self.w = w
        self.h = h
        self.invert = invert
        self.interval = interval
        self.char = char[0]
        self.imgPlot = np.zeros((self.h, self.w, 3), np.uint8)
        self.imgPlot[:] = 225, 225, 225
        self.xP = 0
        self.yP = 0
        self.yList = []
        self.xList = [x for x in range(0, 100)]
        self.ptime = 0

    def update(self, y, color=(255, 0, 255)):
        """
        Update the plot with a new y-value.

        :param y: The new y-value to plot
        :param color: RGB color for the plot line

        :return: Updated image of the plot
        """

        # Check if enough time has passed for an update
        if time.time() - self.ptime > self.interval:
            self.imgPlot[:] = 225, 225, 225  # Refresh
            self.drawBackground()  # Draw static parts
            cv.putText(self.imgPlot, str(y), (self.w - 125, 50), cv.FONT_HERSHEY_PLAIN, 3, (150, 150, 150), 3)

            # Interpolate y-value to plot height
            if self.invert:
                self.yP = int(np.interp(y, self.yLimit, [self.h, 0]))
            else:
                self.yP = int(np.interp(y, self.yLimit, [0, self.h]))

            self.yList.append(self.yP)
            if len(self.yList) == 100:
                self.yList.pop(0)

            # Draw plot lines
            for i in range(2, len(self.yList)):
                x1 = int((self.xList[i - 1] * (self.w // 100)) - (self.w // 10))
                y1 = self.yList[i - 1]
                x2 = int((self.xList[i] * (self.w // 100)) - (self.w // 10))
                y2 = self.yList[i]
                cv.line(self.imgPlot, (x1, y1), (x2, y2), color, 2)

            self.ptime = time.time()

        return self.imgPlot

    def drawBackground(self):
        """
        Draw the static background elements of the plot.
        """

        cv.rectangle(self.imgPlot, (0, 0), (self.w, self.h), (0, 0, 0), cv.FILLED)
        cv.line(self.imgPlot, (0, self.h // 2), (self.w, self.h // 2), (150, 150, 150), 2)

        # Draw grid lines and y-axis labels
        for x in range(0, self.w, 50):
            cv.line(self.imgPlot, (x, 0), (x, self.h), (50, 50, 50), 1)
        for y in range(0, self.h, 50):
            cv.line(self.imgPlot, (0, y), (self.w, y), (50, 50, 50), 1)
            y_label = int(self.yLimit[1] - ((y / 50) * ((self.yLimit[1] - self.yLimit[0]) / (self.h / 50))))
            cv.putText(self.imgPlot, str(y_label), (10, y), cv.FONT_HERSHEY_PLAIN, 1, (150, 150, 150), 1)

        cv.putText(self.imgPlot, self.char, (self.w - 100, self.h - 25), cv.FONT_HERSHEY_PLAIN, 5, (150, 150, 150), 5)

class CvFpsCalc(object):
    def __init__(self, buffer_len=1):
        self._start_tick = cv.getTickCount()
        self._freq = 1000.0 / cv.getTickFrequency()
        self._difftimes = deque(maxlen=buffer_len)

    def get(self):
        current_tick = cv.getTickCount()
        different_time = (current_tick - self._start_tick) * self._freq
        self._start_tick = current_tick

        self._difftimes.append(different_time)

        fps = 1000.0 / (sum(self._difftimes) / len(self._difftimes))
        fps_rounded = round(fps, 2)

        return fps_rounded
