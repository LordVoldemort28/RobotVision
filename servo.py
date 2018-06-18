import sys
import io
import time
import serial
import camera_detection as camera


ser1 = serial.Serial('/dev/ttyACM0', 115200,
        timeout = 0, parity = serial.PARITY_NONE,
        stopbits = serial.STOPBITS_ONE,
        bytesize = serial.EIGHTBITS)

while True:
    print('Loop')
    d = ser1.readline()
    G = b'GO'
    if G in d:
        print('Passed Go')
##        values = camera.give_me_some_numbers()
       
        s = "2;1;0;1;0;"
	ser1.write(s)
        break
    
