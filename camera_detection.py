from collections import deque
import numpy as np
from picamera import PiCamera
from picamera.array import PiRGBArray
import argparse
import sys
import imutils
import cv2
import urllib
import time


class Section():

	def __init__(self, x_min, x_max, y_min, y_max):
		self.color = 'none'
		self.x_min = x_min
		self.x_max = x_max
		self.y_min = y_min
		self.y_max = y_max

	def set_color(self, change_color):
		set_color = change_color

section = [Section] * 4
section_done = [False] * 4


def in_range(variable, num1, num2):
	if num1 <= variable <= num2:
		return True
	else:
		return False

def color_ascii(color):
    if color == 'red':
        return 82
    elif color == 'green':
        return 71
    else:
        return 66

def setting_section(resolution_width, resolution_length):
	section[0] = Section(0, resolution_width/2, 0, resolution_length/2)
	section[1] = Section(resolution_width/2, resolution_width, 0, resolution_length/2)
	section[2] = Section(0, resolution_width/2, resolution_length/2, resolution_length)
	section[3] = Section(resolution_width/2, resolution_width, resolution_length/2, resolution_length)
            
def print_each_section(x, y, color):

	for i in range(0,4):
		if section_done[i] == False and in_range(x, section[i].x_min, section[i].x_max) == True and in_range(y, section[i].y_min, section[i].y_max) == True:
                    section[i].set_color(color)
                    section_done[i] = True
                    print((i+1), x, y, color)
                    convert = {(i+1, color)}
                    return convert
        return None
    
                 
                            
                            

def camera_function():
	#lower = {'red':(0, 150, 145), 'green':(66, 122, 129), 'blue':(97, 100, 117)}
        #upper = {'red':(8,255,255), 'green':(86,255,255), 'blue':(117,255,255)}
	#lower = {'red':(0, 150, 145), 'green':(40,105,95), 'blue':(95,85,90)}
	#upper = {'red':(8,255,255), 'green':(85,245,255), 'blue':(255,255,255)}
        
        lower = {'red':(0, 120, 95), 'green':(66,122,129), 'blue':(97, 100, 117)}
        upper = {'red':(68,255,255), 'green':(86,255,255), 'blue':(117,255,255)}
        
        #Final Values Red - lower(0,120,95) upper(68,255,255)
        #Green Values - lower(40,100,70) upper(125,255,255)
        #Blue Values - lower()
        
	colors = {'red':(0,0,255), 'green':(0,255,0), 'blue':(255,0,0)}
	camera = PiCamera()


	#Set Resolution 
	camera_resolution_width, camera_resolution_length = 1024, 720
	setting_section(camera_resolution_width, camera_resolution_length)

	camera.resolution = (camera_resolution_width, camera_resolution_length)
	camera.framerate = 24
	rawCapture = PiRGBArray(camera, size=(1024, 720))
	
	
        #Setting up the timer
	timeout = time.time() + 5
	final_value = {}
	for image in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
                
                times = 0
                
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
                        if radius > 5:
                            cv2.circle(frame, (int(x), int(y)), int(radius), colors[key], 2)
	                    cv2.putText(frame,key + " ball", (int(x-radius),int(y-radius)), cv2.FONT_HERSHEY_SIMPLEX, 0.6,colors[key],2)
	                    value = print_each_section(center[0], center[1], key)
##		cv2.imshow("Frame", frame)
##	cv2.imshow("Mask", mask)
		rawCapture.truncate(0)
		if value != None:
                    final_value += str(value)
                     
		if time.time() > timeout:
                    break
		times -= 1
        cv2.destroyAllWindows()
        return final_value 
        
def give_me_some_numbers():
    
    numbers = camera_function()
    print(numbers)
    return numbers
    
 
    
    
    
	

    