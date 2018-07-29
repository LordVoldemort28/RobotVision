import sys
import io
import time
import serial
import subprocess
from subprocess import call
import final_version as camera


#TO add this file in bash script
#sudo nano .bashrc
#add python ./Desktop/Robot_Vision/servo.py

'''

offset,camPOs
;offset,camPOS;
where
offset: int
camPos: 1(right) or 0(left)
'''


def servo_file_function():
    ser1 = serial.Serial('/dev/ttyACM0', 115200,
            timeout = 0, parity = serial.PARITY_NONE,
            stopbits = serial.STOPBITS_ONE,
            bytesize = serial.EIGHTBITS)

    while True:
        d = ser1.readline()
        
        
        if d != '':
            if len(d) is 5 or len(d) is 6:
                print('Passed Go')
                
                file = open('package_from_audrino.txt', 'a')
                file.write(d+'\n')
                file.close()
                
                print(d+'\n')
                
                try:
                    value = d.replace(';','')
                    data = value.split(',')
                    distance_from_board, side = data[0], data[1]
                except:
                    print('Shit Package')
                    servo_file_function()
                    
                try:
                    #time.sleep(2)
                    print('Camera Run')
                    
                    values = camera.give_me_some_numbers(distance_from_board, side)
                    ser1.write(values)
                    print(values+'\n')
                except:
                    continue
            else:
                servo_file_function()
                
#Arduino SA Mega
def check_usb():
    
    p = subprocess.Popen("lsusb", stdout = subprocess.PIPE, shell=True)
    
    output = p.communicate()
    console_output = str(output).split(' ')
    
    flag = False
    for each_word in console_output:
        #print(each_word)
        if each_word =='Arduino':
            print('Yes')
            servo_file_function()
            
            flag = True
    if flag is False:
        print('Wating for usb to connect..........')
        check_usb()
    
    
check_usb()
            

    
