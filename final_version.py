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
import re
import csv

class Section():

    def __init__(self, x_min, x_max, y_min, y_max):
		self.color = None
		self.x = None
		self.y = None
		self.radius = None
		self.x_min = x_min
		self.x_max = x_max
		self.y_min = y_min
		self.y_max = y_max

    def set_color(self, change_color):
    	self.color = change_color
            
    def set_radius(self, radius):
        self.radius = radius
                
    def set_x(self, x):
        self.x = x
                    
    def set_y(self, y):
        self.y = y

    def get_radius(self):
        return self.radius

    def get_color(self):
        return self.color
            
    def get_ascii_color(self):
        return ascii_color(self.color)
                    
    def get_x(self):
        return self.x
                
    def get_y(self):
        return self.y
        


section = [Section] * 4
section_done = [False] * 4

def in_range(variable, num1, num2):
	if num1 <= variable <= num2:
		return True
	else:
		return False
	    
def ascii_color(color):
    if color == 'red':
        return '0'
    elif color == 'green':
        return '1'
    elif color == 'blue' :
        return '2'
    else:
        return None

def setting_section(resolution_width, resolution_length):
	section[0] = Section(0, resolution_width/2, 0, resolution_length/2)
	section[1] = Section(resolution_width/2, resolution_width, 0, resolution_length/2)
	section[2] = Section(0, resolution_width/2, resolution_length/2, resolution_length)
	section[3] = Section(resolution_width/2, resolution_width, resolution_length/2, resolution_length)
	
def print_each_section(pixel_x, pixel_y, color, radius):
    
    for i in range(0,4):
        if section_done[i] == False and in_range(pixel_x, section[i].x_min, section[i].x_max) == True and in_range(pixel_y, section[i].y_min, section[i].y_max):
            section[i].set_color(color)
            section_done[i] = True
            section[i].set_x(pixel_x)
            section[i].set_y(pixel_y)
            section[i].set_radius(radius)
            #print((i+1), pixel_x, pixel_y, color)
        
    
	
def camera_function():
    #Setting up color boundaries   
        lower = {'red':(0, 120, 95), 'green':(66,122,129), 'blue':(97, 100, 117)}
        upper = {'red':(68,255,255), 'green':(86,255,255), 'blue':(117,255,255)}
        #lower = {'red':(0, 150, 145), 'green':(40, 105, 95), 'blue':(95, 85, 90)}
        #upper = {'red':(8,255,255), 'green':(86,245,255), 'blue':(117,255,255)}


        colors = {'red':(0,0,255), 'green':(0,255,0), 'blue':(255,0,0)}
    
    
    #Set Resolution and camera properties
        camera = PiCamera()
        
	camera_resolution_width, camera_resolution_length = 640, 480
	#Setting up the section pixel boundaries 
	setting_section(camera_resolution_width, camera_resolution_length)

	camera.resolution = (camera_resolution_width, camera_resolution_length)
	camera.framerate = 24
	rawCapture = PiRGBArray(camera, size=(camera_resolution_width, camera_resolution_length))
	
    
    #Setting up the timer
	timeout = time.time() + 5
	
	final_value = []
	
            
	
        for image in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
                
                #Starting the timer 
                timer = 0
            
                frame = image.array
		frame = imutils.resize(frame, width=600)
		blurred = cv2.GaussianBlur(frame, (11, 11), 0)
	    	hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
                
                for key, value in upper.items():
                    kernel = np.ones((5,5),np.uint8)
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
	                    print_each_section(center[0], center[1], key, radius)
	                    with open('pixel_coordinates2.csv', 'a') as newFile:
                                newFileWriter = csv.writer(newFile)
                                newFileWriter.writerow([radius*2, center[0], center[1], key, radius])
	                
            
                cv2.imshow("Mask", mask)
                cv2.imshow("Frame", frame)
                rawCapture.truncate(0)
                   
                    
                if time.time() > timeout:
                    break
		timer -= 1
	
        cv2.destroyAllWindows()
        
def write_values_to_excel():
    with open('section_coordinates.csv', 'a') as newFile:
                                newFileWriter = csv.writer(newFile)
                                newFileWriter.writerow(['*************'])
    
    for i in range(0,4):
        with open('section_coordinates.csv', 'a') as newFile2:
                                newFileWriter2 = csv.writer(newFile2)
                                newFileWriter2.writerow([(i+1), section[i].get_x(), section[i].get_y(), section[i].get_color()])
        print((i+1), section[i].get_x(), section[i].get_y(), section[i].get_color())

def formatter_for_audrino(color, x_robotic_arm, y_robotic_arm, z_robotic_arm):
    return str(color)+','+str(round(x_robotic_arm,2))+','+str(round(y_robotic_arm,2))+','+str(round(z_robotic_arm,2))+';'

        
def coordinates_calculator(side, x_robotics):
    #Diameter Average is 102
    #Ratio to pixel average by inch diameter 122/1.57 = 77.70
    PIXEL_TO_INCH_WIDTH = 8.23 #640/77.70
    PIXEL_TO_INCH_HIEGHT = 6.24  #480/77.70
    DIAMETER_RATIO =77.70 #81.3
    
    #Translation from camera to robotic arm
    x_translation = 0
    y_translation = 4.875
    z_translation = 6
    
    x_robotics = 7.50
    z_camera = 7.50

    no_ball = True
    format =';'
    
    #if in_range(x, 19, 20) == True:
    for i in range(0, 4):
        formatted_coordinates =''
        if section[i].get_color() != None:
            no_ball = False
            
            formatted_coordinates =''
            if side == 1:
                z_camera = -z_camera
            x_camera = float(section[i].get_x()) / DIAMETER_RATIO
            y_camera = PIXEL_TO_INCH_HIEGHT - (float(section[i].get_y()) / DIAMETER_RATIO)
            
            x_robotic_arm = (-z_camera) + x_translation
            y_robotic_arm = x_camera + y_translation
            z_robotic_arm = (-y_camera) + z_translation +3.5

            color = section[i].get_ascii_color()
            formatted_coordinates = formatter_for_audrino(color, x_robotic_arm, y_robotic_arm, z_robotic_arm)
        
        format += formatted_coordinates

    if no_ball == True:
        return ';404;'
    else:
        return format
    
def give_me_some_numbers(string_value):
    
    #Data splitting from audrino
    value = string_value.replace(";","")
    data = value.split(',')
    side, distance_from_board = data[0], data[1]
    
    with open('pixel_coordinates.csv', 'a') as newFile:
                                newFileWriter = csv.writer(newFile)
                                newFileWriter.writerow(['*************'])
    
    #Starting Image processing 
    camera_function()
    
    #Passing format coordinates
    format = coordinates_calculator(side, distance_from_board)    

    #Writing results to excel file
    write_values_to_excel()

    #Writing format in text file 
##    file = open('format_storage', 'a')
##    file.write(format+'\n')
##    file.close()

    return format
    

print(give_me_some_numbers(';0,30;'))
    


