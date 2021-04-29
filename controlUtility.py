import time
import datetime
import RPi.GPIO as gpio
import os
import math
import serial


class Controls:

    def __init__(self):
        self.isIMUEnabled = True
        self.isUltraEnabled = True
        self.imuValue = 0.00
        self.distance = 0.00
        self.file = open("map_info.txt",'a')

    def getIMUReading(self):
        return self.imuValue

    def getDistance(self):
        return self.distance

    def enableDisableIMU(self, status):
        self.isIMUEnabled = status

    def enableDisableUltrasonic(self, status):
        self.isUltraEnabled = status

    def IMUReading(self, _):
        ser = serial.Serial('/dev/ttyUSB0', 9600)
        
        count = 0

        while self.isIMUEnabled:
            if (ser.in_waiting > 0):
                count += 1        
                #Read serial stream
                line = ser.readline()        
                #Avoid first n-lines of serial information
                if count>5:            
                    #Strip serial stream of extra characters
                    line = line.rstrip().lstrip()            
                    line = str(line)
                    line = line.strip("'")
                    line = line.strip("b'")
                    self.imuValue = float(line)


    def distanceReading(self, _):
        trig = 16
        echo = 18
        
        while self.isUltraEnabled:

            count = 0
            distance = 0.0

            while count < 3:
                gpio.setmode(gpio.BOARD)
                gpio.setup(trig, gpio.OUT)
                gpio.setup(echo, gpio.IN)
            
                #Ensure outout has no value
                gpio.output(trig, False)
                time.sleep(0.01)

                #Generate Trigger pulse
                gpio.output(trig, True)
                time.sleep(0.00001)
                gpio.output(trig, False)

                #Generate Echo time signal
                while gpio.input(echo) == 0:
                    pulse_start = time.time()

                while gpio.input(echo) == 1:
                    pulse_end = time.time()

                #clear the output pins
                gpio.cleanup()
                pulse_duration = pulse_end - pulse_start

                #Convert time to distance
                distance = distance + pulse_duration*17150
                count = count + 1

            self.distance = round((distance/3), 2) #taking average distance
            
            
            
    #forwardCount = 0
    ##### INit the pins
    def setupPins():
        gpio.setmode(gpio.BOARD)
        gpio.setup(31, gpio.OUT)
        gpio.setup(33, gpio.OUT)
        gpio.setup(35, gpio.OUT)
        gpio.setup(37, gpio.OUT)
        gpio.setup(36, gpio.OUT)
        gpio.output(36, False)
        #gpio.setup(7, gpio.IN, pull_up_down = gpio.PUD_UP)
        #gpio.setup(12, gpio.IN, pull_up_down = gpio.PUD_UP)
        
    def clearPins():
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
        

    def forward(self, maxTicks):
        setupPins()
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
                clearPins()
                self.file.write(str(self.imuValue)+','+str(maxTicks/98)+'\n')
                break
            
    def reverse(self, maxTicks):
        setupPins()
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
                clearPins()
                self.file.write(str(self.imuValue)+','+str(maxTicks/98)+'\n')
                break

        
    def pivotright(angle):
        setupPins()
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
        
        # if ser.in_waiting > 0:
        #     line = ser.readline() #print(line)
        #     line = line.rstrip().lstrip()
        #     line = str(line)
        #     line = line.strip("'")
        #     line = line.strip("b'")

        goalAngle = (self.imuValue + angle)%360


        while True:
            #Read serial stream
            # line = ser.readline() #print(line)
            # line = line.rstrip().lstrip()
            # line = str(line)
            # line = line.strip("'")
            # line = line.strip("b'")
            currAngle = self.imuValue#float(line)
           
            if int(gpio.input(12)) != int(buttonBR):
                buttonBR = int(gpio.input(12))
                counterBR += 1
                
            if int(gpio.input(7)) != int(buttonFL):
                buttonFL = int(gpio.input(7))
                counterFL += 1

            if currAngle+offset >= goalAngle and currAngle-offset <= goalAngle:
                pwm1.stop()
                pwm2.stop()
                clearPins()
                break


    def pivotleft(angle):
        setupPins()
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
        
        # if ser.in_waiting > 0:
        #     line = ser.readline() 
        #     line = line.rstrip().lstrip()
        #     line = str(line)
        #     line = line.strip("'")
        #     line = line.strip("b'")
        #     goalAngle = (float(line) - angle)%360
        goalAngle = (self.imuValue + angle)%360

        while True:
            # line = ser.readline() 
            # line = line.rstrip().lstrip()
            # line = str(line)
            # line = line.strip("'")
            # line = line.strip("b'")
            currAngle = self.imuValue #float(line)
            
            if int(gpio.input(12)) != int(buttonBR):
                buttonBR = int(gpio.input(12))
                counterBR += 1
                
            if int(gpio.input(7)) != int(buttonFL):
                buttonFL = int(gpio.input(7))
                counterFL += 1

            if currAngle+offset >= goalAngle and currAngle-offset <= goalAngle:
                pwm1.stop()
                pwm2.stop()
                clearPins()
                break