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

    """ Section class contain the area of section in the whole image and after the detection of ball in 
        particular section it stores the color, radius of ball and pixel x and y values """

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
        

"""
Creating section object 
"""
section = [Section] * 4
section_done = [False] * 4


"""
In range funtion classify that particular variable falls in range or not
"""
def in_range(variable, num1, num2):
	if num1 <= variable <= num2:
		return True
	else:
		return False

"""
Converting color to format for robotic arm (0,1,2 - Red, Green, Blue)
"""
def ascii_color(color):
    if color == 'red':
        return '0'
    elif color == 'green':
        return '1'
    elif color == 'blue' :
        return '2'
    else:
        return None

""" 0,0         width/2         width
    +++++++++++++++++++++++++++++
    |             |             |
    |      1      |      2      |
    |             |             !
    +++++++++++++++++++++++++++++length/2
    |             |             |
    |      3      |      4      |
    |             |             |
    +++++++++++++++++++++++++++++length

    Section division on the basis of resolution width and length

"""
def setting_section(resolution_width, resolution_length):
	section[0] = Section(0, resolution_width/2, 0, resolution_length/2)
	section[1] = Section(resolution_width/2, resolution_width, 0, resolution_length/2)
	section[2] = Section(0, resolution_width/2, resolution_length/2, resolution_length)
	section[3] = Section(resolution_width/2, resolution_width, resolution_length/2, resolution_length)
        

"""
Print each section takes value from image processing and check pixels for section division. 
It also store valid color, radius and pixel x and y coordinates 
"""	
def print_each_section(pixel_x, pixel_y, color, radius):
    
    for i in range(0,4):
        if section_done[i] == False and in_range(pixel_x, section[i].x_min, section[i].x_max) == True and in_range(pixel_y, section[i].y_min, section[i].y_max) == True:
            section[i].set_color(color)
            section_done[i] = True
            section[i].set_x(pixel_x)
            section[i].set_y(pixel_y)
            section[i].set_radius(radius)

        
"""
Main image processing funtion

"""
def camera_function():
    #Setting up color boundaries
        lower = {'red':(0, 150, 145), 'green':(50, 100, 100), 'blue':(95, 85, 90)}
        upper = {'red':(8,255,255), 'green':(70,255,255), 'blue':(117, 255, 255)}
        #lower = {'red':(0, 120, 95), 'green':(66,122,129), 'blue':(97, 100, 117)}
        #upper = {'red':(68,255,255), 'green':(86,255,255), 'blue':(117,255,255)}
        #lower = {'red':(0, 150, 145), 'green':(40, 105, 95), 'blue':(95, 85, 90)}
        #upper = {'red':(8,255,255), 'green':(86,245,255), 'blue':(117,255,255)}


        colors = {'red':(0,0,255), 'green':(0,255,0), 'blue':(255,0,0)}
    
    
    #Set Resolution and camera properties
        camera = PiCamera()
    
	camera_resolution_width, camera_resolution_length = 1024, 720
	#Setting up the section pixel boundaries 
	setting_section(camera_resolution_width, camera_resolution_length)

	camera.resolution = (camera_resolution_width, camera_resolution_length)
	camera.framerate = 15
	rawCapture = PiRGBArray(camera, size=(camera_resolution_width, camera_resolution_length))
	
    
    #Setting up the timer for 5 sec 
	timeout = time.time() + 2
	        
	   #Taking every image from picam to process
        for image in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
                
                #Starting the timer 
                timer = 0
            
                frame = image.array
##		frame = imutils.resize(frame, width=640)
		blurred = cv2.GaussianBlur(frame, (11, 11), 0)
	    	hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
                
                #Masking for balls for each color red, blue and green according to their threshold values
                for key, value in upper.items():
                    kernel = np.ones((5,5),np.uint8)
                    mask = cv2.inRange(hsv, lower[key], upper[key])
                    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
                    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
		    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[-2]
                    center = None
                
			         #Checking contouring of a circle 
                    if len(cnts) > 0:
                        c = max(cnts, key=cv2.contourArea)
                        ((x, y), radius) = cv2.minEnclosingCircle(c)
                        M = cv2.moments(c)
                        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                        #If the the circle radius is bigger than 5 
                        if radius > 5:
                            cv2.circle(frame, (int(x), int(y)), int(radius), colors[key], 2)
	                    cv2.putText(frame,key + " ball", (int(x-radius),int(y-radius)), cv2.FONT_HERSHEY_SIMPLEX, 0.6,colors[key],2)
	                    
                        #Sending values to store them 
                            print_each_section(center[0], center[1], key, radius)
                rawCapture.truncate(0)
                   
                    
                if time.time() > timeout:
                    break
		timer -= 1
	
        cv2.destroyAllWindows()
        camera.stop_preview()
        camera.close()

def print_section():
    for i in range(0,4):
        print(str(i+1)+' '+str(section[i].get_x())+' '+str(section[i].get_y())+' '+str(section[i].get_color()+'\n'))
        
def write_values_to_text(side):
    if side is -1:

        text_file = open('side_'+side+'.txt', 'a') 
        text_file.write(section[0].get_ascii_color()+';'+section[2].get_ascii_color()+';\n')
        text_file.write(section[1].get_ascii_color()+';'+section[3].get_ascii_color()+';\n')
    else:
        text_file = open('side_'+side+'.txt', 'a') 
        text_file.write(section[1].get_ascii_color()+';'+section[3].get_ascii_color()+';\n')
        text_file.write(section[0].get_ascii_color()+';'+section[1].get_ascii_color()+';\n')
    
    text_file.close()
""" Formatter for audrino :color,x_r,y_r,z_r:
"""

#Y = 6.64, 1.64
def coordinates_calculator(side, x_robotics):

    side = int(side)
    no_ball = True
    format =';'

    right[4] = ['8.60,7.40,10.50;', '7.90,1.20,10.50;', '8.10,6.40,7.00;', '7.80,1.20,7.00;']
    left[4] = ['-8.00,1.20,10.50;', '-8.20,6.40,10.50', '-7.80,1.20,7.00;', '-8.00,6.20,7.00;']
  
    
    #if in_range(x, 19, 20) == True:
    for i in range(0, 4):
        
        formatted_coordinates =''
        if section[i].get_color() != None:
            #y = 640 - float(section[i].get_x()) 
            no_ball = False
            
            formatted_coordinates =''
            color = section[i].get_ascii_color()
            if side is -1:
                formatted_coordinates += str(color)+','+left[i]
            else:
                formatted_coordinates += str(color)+','+right[i]

            
        
        format += formatted_coordinates

    if no_ball == True:
        return ';404;'
    else:
        return format
    
def give_me_some_numbers(distance_from_board, side):
    

    
    #Starting Image processing 	
    if side != 0:
        camera_function()

    #Print Result
    print_section()
    
    #Passing format coordinates
    format = coordinates_calculator(side, distance_from_board)    

    #Writing results to excel file
    write_values_to_excel()

    #Writing format in text file 
    file = open('format_storage', 'a')
    file.write(format+'\n')
    file.close()
    
    for i in range(0,4):
        section_done[i] = False
    
    return format
    

#print(give_me_some_numbers(1,-1))



