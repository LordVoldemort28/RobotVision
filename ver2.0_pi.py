from collections import deque
import numpy as np
from picamera import PiCamera
from picamera.array import PiRGBArray
import argparse
import sys
import imutils
import cv2
import urllib

section = []
section_done = [false, false, false, false]

class Section():

	def __init__(self, x_min, x_max, y_min, y_max):
		self.color = 'none'
		self.x_min = x_min
		self.x_max = x_max
		self.y_min = y_min
		self.y_max = y_max

	def set_color(self, change_color):
		set_color = change_color

def in_range(variable, num1, num2):
	if num1 <= variable <= num2:
		return true
	else
		return false 

def setting_section(resolution_width, resolution_length):
	section[0] = Section(0, resolution_width/2, 0, resolution_length/2)
	section[1] = Section(resolution_width/2, resolution_width, 0, resolution_length/2)
	section[2] = Section(0, resolution_width/2, resolution_length/2, resolution_length)
	section[3] = Section(resolution_width/2, resolution_width, resolution_length/2, resolution_length)

def print_each_section(x, y, color):

	for i in range(0,4):
		if(section_done[i] == false &&in_range(x, section[i].x_min, section[i].x_max) == true && in_range(y, section[i].y_min, section.[i].y_max) == true):
			section[i].set_color(color)
			section_done[i] = true
			print((i+1), x, y, key) 

def main():
	##lower = {'red':(166, 84, 141), 'green':(66, 122, 129), 'blue':(97, 100, 117)}
	##upper = {'red':(186,255,255), 'green':(86,255,255), 'blue':(117,255,255)}
	lower = {'red':(0, 150, 145), 'green':(40,105,95), 'blue':(95,85,90)}
	upper = {'red':(8,255,255), 'green':(85,245,255), 'blue':(255,255,255)}
	colors = {'red':(0,0,255), 'green':(0,255,0), 'blue':(255,0,0)}
	camera = PiCamera()

	#Set Resolution 
	camera_resolution_width, camera_resolution_length = 1024, 720
	setting_section(camera_resolution_width, camera_resolution_length)

	camera.resolution = (camera_resolution_width, camera_resolution_length)
	camera.framerate = 24
	rawCapture = PiRGBArray(camera, size=(1024, 720))
	for image in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	        frame = image.array
		frame = imutils.resize(frame, width=600)
		blurred = cv2.GaussianBlur(frame, (11, 11), 0)
	    	hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
		for key, value in upper.items():
			kernel = np.ones((9,9),np.uint8)
	        	mask = cv2.inRange(hsv, lower[key], upper[key])
	        	mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
	        	mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
			cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[-2]
	        	center = None
			
			if len(cnts) > 0:
				c = max(cnts, key=cv2.contourArea)
	            		((x, y), radius) = cv2.minEnclosingCircle(c)
	           		M = cv2.moments(c)
	            		center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
				if radius > 0.5:
	                                cv2.circle(frame, (int(x), int(y)), int(radius), colors[key], 2)
	                                cv2.putText(frame,key + " ball", (int(x-radius),int(y-radius)), cv2.FONT_HERSHEY_SIMPLEX, 0.6,colors[key],2)
	                                print_each_section(center[0], center[1], key)
	#                            cv2.circle(frame, (int(x), int(y)), int(radius), colors[key], 2)
	#                            cv2.circle(frame, center, 3, (0, 0, 255), -1)
	#                            cv2.putText(frame,key + " ball", (int(x-radius),int(y-radius)), cv2.FONT_HERSHEY_SIMPLEX, 0.6,colors[key],2)
	#                            cv2.putText(frame,"("+str(center[0])+","+str(center[1])+")", (center[0]+10,center[1]+15), cv2.FONT_HERSHEY_SIMPLEX, 0.4,(0, 0, 255),1)
	#                            print(key, center[0], center[1])
		cv2.imshow("Frame", frame)
		cv2.imshow("Mask", mask)
		rawCapture.truncate(0)
		key = cv2.waitKey(1) & 0xFF
		if key == ord("q"):
			break
	cv2.destroyAllWindows()

 
if __name__ == '__main__':
    main()
