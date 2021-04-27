import time
import datetime
import RPi.GPIO as gpio
import os
import math
import serial
import emailIntegration as EMAIL

#Indentify serial communication
ser = serial.Serial('/dev/ttyUSB0', 9600)

forwardCount = 0
##### INit the pins
def init():
    gpio.setmode(gpio.BOARD)
    gpio.setup(31, gpio.OUT)
    gpio.setup(33, gpio.OUT)
    gpio.setup(35, gpio.OUT)
    gpio.setup(37, gpio.OUT)
    gpio.setup(36, gpio.OUT)
    gpio.output(36, False)
    gpio.setup(7, gpio.IN, pull_up_down = gpio.PUD_UP)
    gpio.setup(12, gpio.IN, pull_up_down = gpio.PUD_UP)
    
def gameover():
    gpio.output(31, False)
    gpio.output(33, False)
    gpio.output(35, False)
    gpio.output(37, False)
    gpio.cleanup()
    
def closeGripper():
    gpio.setmode(gpio.BOARD)
    gpio.setup(36, gpio.OUT)  #Gripper
    
    pwm = gpio.PWM(36, 50)
    pwm.start(5)
    
    rate = 0.15
    duty = float(3.5)
    while True:
        duty += rate
        pwm.ChangeDutyCycle(duty)
        time.sleep(0.2)
        if duty >= 6.5:#6.25:
            break
    pwm.stop()
    #clear the output pins
    gpio.output(36, False)
    gpio.cleanup()

def openGripper():
    gpio.setmode(gpio.BOARD)
    gpio.setup(36, gpio.OUT)  #Gripper
    
    pwm = gpio.PWM(36, 50)
    pwm.start(5)
    
    rate = 0.15
    duty = float(6)
    while True:
        pwm.ChangeDutyCycle(duty)
        duty -= rate        
        time.sleep(0.2)
        if duty <= 3.5:
            break
    pwm.stop()
    #clear the output pins
    gpio.output(36, False)
    gpio.cleanup()
    
def forward(maxTicks):
    init()
    counterBR = np.uint64(0)
    counterFL = np.uint64(0)

    buttonBR = int(0)
    buttonFL = int(0)

    # Initialize pwm signal to control motor
    pwm1 = gpio.PWM(37, 50) #Right side
    pwm2 = gpio.PWM(31, 50) #Left side
    val = 40
    pwm1.start(val)
    pwm2.start(val)
    time.sleep(0.1)


    while True:      
        if int(gpio.input(12)) != int(buttonBR):
            buttonBR = int(gpio.input(12))
            counterBR += 1
            
        if int(gpio.input(7)) != int(buttonFL):
            buttonFL = int(gpio.input(7))
            counterFL += 1
            
        if counterBR >= maxTicks:
            pwm1.stop()
            
        if counterFL >= maxTicks:
            pwm2.stop()
            
        if counterFL >= maxTicks and counterBR >= maxTicks:
            pwm1.stop()
            pwm2.stop()
            gameover()
            #Read serial stream
            #line = ser.readline() #print(line)
            #line = line.rstrip().lstrip()
            #line = str(line)
            #line = line.strip("'")
            #line = line.strip("b'")
            #print(line)
        
            #Return float
            #currAngle = float(line)
            #file.write(str(currAngle)+'\n')
            #file.write(str(currAngle)+','+str(maxTicks/98)+'\n')
            break
        
def reverse(maxTicks):
    init()
    counterBR = np.uint64(0)
    counterFL = np.uint64(0)

    buttonBR = int(0)
    buttonFL = int(0)

    # Initialize pwm signal to control motor
    pwm1 = gpio.PWM(33, 50) #Right side
    pwm2 = gpio.PWM(35, 50) #Left side
    val = 40
    pwm1.start(val)
    pwm2.start(val)
    time.sleep(0.1)


    while True:
        if int(gpio.input(12)) != int(buttonBR):
            buttonBR = int(gpio.input(12))
            counterBR += 1
            
        if int(gpio.input(7)) != int(buttonFL):
            buttonFL = int(gpio.input(7))
            counterFL += 1
            
        if counterBR >= maxTicks:
            pwm2.stop()
            
        if counterFL >= maxTicks:
            pwm1.stop()
            
        if counterFL >= maxTicks and counterBR >= maxTicks:
            pwm1.stop()
            pwm2.stop()
            gameover()
            #Read serial stream
            #line = ser.readline() #print(line)
            #line = line.rstrip().lstrip()
            #line = str(line)
            #line = line.strip("'")
            #line = line.strip("b'")
            #print(line)
        
            #Return float
            #currAngle = float(line)
            #file.write(str(currAngle)+'\n')
            #file.write(str(currAngle)+','+str(maxTicks/98)+'\n')
            break

    
def pivotright(angle):
    init()
    offset = 1 #degrees
    counterBR = np.uint64(0)
    counterFL = np.uint64(0)

    buttonBR = int(0)
    buttonFL = int(0)

    # Initialize pwm signal to control motor
    pwm1 = gpio.PWM(31, 50) #Right side
    pwm2 = gpio.PWM(35, 50) #Left side
    val = 35
    pwm1.start(val)
    pwm2.start(val)
    time.sleep(0.1)
    
    if ser.in_waiting > 0:
        line = ser.readline() #print(line)
        line = line.rstrip().lstrip()
        line = str(line)
        line = line.strip("'")
        line = line.strip("b'")
        goalAngle = (float(line) + angle)%360


    while True:
        #Read serial stream
        line = ser.readline() #print(line)
        line = line.rstrip().lstrip()
        line = str(line)
        line = line.strip("'")
        line = line.strip("b'")
        currAngle = float(line)
       
        if int(gpio.input(12)) != int(buttonBR):
            buttonBR = int(gpio.input(12))
            counterBR += 1
            
        if int(gpio.input(7)) != int(buttonFL):
            buttonFL = int(gpio.input(7))
            counterFL += 1

        if currAngle+offset >= goalAngle and currAngle-offset <= goalAngle:
            pwm1.stop()
            pwm2.stop()
            gameover()
            break


def pivotleft(angle):
    init()
    offset = 1 #degrees
    counterBR = np.uint64(0)
    counterFL = np.uint64(0)

    buttonBR = int(0)
    buttonFL = int(0)

    # Initialize pwm signal to control motor
    pwm1 = gpio.PWM(33, 50) #Right side
    pwm2 = gpio.PWM(37, 50) #Left side
    val = 35
    pwm1.start(val)
    pwm2.start(val)
    time.sleep(0.1)
    
    if ser.in_waiting > 0:
        line = ser.readline() 
        line = line.rstrip().lstrip()
        line = str(line)
        line = line.strip("'")
        line = line.strip("b'")
        goalAngle = (float(line) - angle)%360

    while True:
        line = ser.readline() 
        line = line.rstrip().lstrip()
        line = str(line)
        line = line.strip("'")
        line = line.strip("b'")
        currAngle = float(line)
        
        if int(gpio.input(12)) != int(buttonBR):
            buttonBR = int(gpio.input(12))
            counterBR += 1
            
        if int(gpio.input(7)) != int(buttonFL):
            buttonFL = int(gpio.input(7))
            counterFL += 1

        if currAngle+offset >= goalAngle and currAngle-offset <= goalAngle:
            pwm1.stop()
            pwm2.stop()
            gameover()
            break