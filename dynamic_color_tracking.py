# python dynamic_color_tracking.py <name_of_color>
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import sys
import argparse
import numpy as np
 
 
def callback(value):
    pass
 
def main():

    camera = PiCamera()
    camera.resolution = (640, 480)
    camera.framerate = 20
    rawCapture = PiRGBArray(camera, size=(640, 480))

    color = sys.argv[1]

    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        image = frame.array
        
        frame_to_thresh = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        if color == 'red':
            v1_min, v2_min, v3_min, v1_max, v2_max, v3_max = 0,150,145,8,255,255
        elif color == 'green':
            v1_min, v2_min, v3_min, v1_max, v2_max, v3_max = 40,105,95,85,245,255
        else:
            v1_min, v2_min, v3_min, v1_max, v2_max, v3_max = 95,85,90,255,255,255
        
 
        thresh = cv2.inRange(frame_to_thresh, (v1_min, v2_min, v3_min), (v1_max, v2_max, v3_max))
 
        kernel = np.ones((5,5),np.uint8)
        mask = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
 
        # find contours in the mask and initialize the current
        # (x, y) center of the ball
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[-2]
        center = None
 
        # only proceed if at least one contour was found
        if len(cnts) > 0:
            # find the largest contour in the mask, then use
            # it to compute the minimum enclosing circle and
            # centroid
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
 
            # only proceed if the radius meets a minimum size
            if radius > 10:
                # draw the circle and centroid on the frame,
                # then update the list of tracked points
                cv2.circle(image, (int(x), int(y)), int(radius),(0, 255, 255), 2)
                cv2.circle(image, center, 3, (0, 0, 255), -1)
                cv2.putText(image,"centroid", (center[0]+10,center[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.4,(0, 0, 255),1)
                cv2.putText(image,"("+str(center[0])+","+str(center[1])+")", (center[0]+10,center[1]+15), cv2.FONT_HERSHEY_SIMPLEX, 0.4,(0, 0, 255),1)
                print(center[0],center[1])
        # show the frame to our screen
        cv2.imshow("Original", image)
        cv2.imshow("Thresh", thresh)
        cv2.imshow("Mask", mask)
        rawCapture.truncate(0)
 
        if cv2.waitKey(1) & 0xFF is ord('q'):
            break
 
 
if __name__ == '__main__':
    main()