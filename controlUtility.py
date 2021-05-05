import time
import RPi.GPIO as gpio
import numpy as np
import serial


class Controls:

    def __init__(self):
        self.isIMUEnabled = True
        self.isUltraEnabled = True
        self.startOrientation = -1
        self.imuValue = 0.00
        self.distance = 0.00
        #self.file = open("map_info.txt",'a')

    def getIMUReading(self):
        return self.imuValue

    def getDistance(self):
        trig = 16
        echo = 18
        try:
            if self.isUltraEnabled:
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

 
                    while gpio.input(echo) == 0: #and lapseCounter <= 20:
                        pulse_start = time.time()
                        
                    while gpio.input(echo) == 1:
                        pulse_end = time.time()

                    #clear the output pins
                    gpio.cleanup()
                    pulse_duration = pulse_end - pulse_start

                    #Convert time to distance
                    distance = distance + pulse_duration*17150
                    count = count + 1

                distance = round((distance/3), 2) #taking average distance
                return(distance)
         
        except Exception as e:
            print(e)

    def enableDisableIMU(self, status):
        self.isIMUEnabled = status

    def enableDisableUltrasonic(self, status):
        self.isUltraEnabled = status

    def IMUReading(self, _):
        ser = serial.Serial('/dev/ttyUSB0', 9600)
        
        count = 0
        try:
            
            while True:
                if self.isIMUEnabled:
                    if (ser.in_waiting > 0):
                        count += 1        
                        #Read serial stream
                        line = ser.readline()        
                        #Avoid first n-lines of serial information
                        if count>10:            
                            #Strip serial stream of extra characters
                            line = line.rstrip().lstrip()            
                            line = str(line)
                            line = line.strip("'")
                            line = line.strip("b'")
                            self.imuValue = float(line)
                            if self.startOrientation == -1:
                                self.startOrientation = float(line)
        except ValueError as e:
            self.IMUReading(_)

    def distanceReading(self, _):
        trig = 16
        echo = 18
        try:
            while True:
                if self.isUltraEnabled:
                    
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
                        #lapseCounter = 0 #to reset if it takes too long
                        #print(self.isUltraEnabled)
                        while gpio.input(echo) == 0: #and lapseCounter <= 20:
                            pulse_start = time.time()
                        
                        #if lapseCounter > 20:
                         #   gpio.cleanup()
                          #  continue
                        #print('here')
                        while gpio.input(echo) == 1:
                            pulse_end = time.time()

                        #clear the output pins
                        gpio.cleanup()
                        pulse_duration = pulse_end - pulse_start

                        #Convert time to distance
                        distance = distance + pulse_duration*17150
                        count = count + 1

                    self.distance = round((distance/3), 2) #taking average distance
                    #print(self.distance)
         
        except Exception as e:
            self.distanceReading(_)
            
    def locateVaccine(self, X, Y, radius):
        degrees = 0
        centerX = int(640/2)
        centerY = int(480/2)
        
        if(X > 290 and X < 350):
            if radius*2 > 400: #the object is close to the gripper
                self.closeGripper()
                return True
            else:
                self.forward(3)
        else:
            if(X < centerX):
                #rotate left
                degrees = (320 - X)*0.061
                self.pivotleft(degrees)
            else:
                #rotate right
                degrees = (640 - X)*0.061
                self.pivotright(degrees)
            
        return False
            
            
    def setupPins(self):
        gpio.setmode(gpio.BOARD)
        gpio.setup(31, gpio.OUT)
        gpio.setup(33, gpio.OUT)
        gpio.setup(35, gpio.OUT)
        gpio.setup(37, gpio.OUT)
        gpio.setup(36, gpio.OUT)
        gpio.output(36, False)
        gpio.setup(7, gpio.IN, pull_up_down = gpio.PUD_UP)
        gpio.setup(12, gpio.IN, pull_up_down = gpio.PUD_UP)
        
    def clearPins(self):
        gpio.output(31, False)
        gpio.output(33, False)
        gpio.output(35, False)
        gpio.output(37, False)
        #gpio.cleanup()
        
    def closeGripper(self):
        print('[INFO] Closing gripper...')
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
        #gpio.cleanup()

    def openGripper(self):
        print('[INFO] Opening gripper...')
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
        #gpio.cleanup()
        

    def forward(self, maxTicks):
        print('[INFO] Moving forward...')
        self.setupPins()
        file = open('map_info.txt','a')
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
                self.clearPins()
                file.write(str(self.getIMUReading())+','+str(maxTicks/98)+'\n')
                file.close()
                break
            
    def reverse(self, maxTicks):
        print('[INFO] Moving backward...')
        self.setupPins()
        file = open('map_info.txt','a')
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
                self.clearPins()
                file.write(str((self.getIMUReading()-180)%360)+','+str(maxTicks/98)+'\n')
                file.close()
                break

        
    def pivotright(self, angle):
        print('[INFO] Turning right...')
        self.setupPins()
        offset = 2 #degrees
        counterBR = np.uint64(0)
        counterFL = np.uint64(0)

        buttonBR = int(0)
        buttonFL = int(0)

        # Initialize pwm signal to control motor
        pwm1 = gpio.PWM(31, 50) #Right side
        pwm2 = gpio.PWM(35, 50) #Left side
        val = 55
        pwm1.start(val)
        pwm2.start(val)
        time.sleep(0.1)

        goalAngle = (self.getIMUReading() + angle)%360


        while (self.getIMUReading()+offset <= goalAngle and self.getIMUReading()-offset >= goalAngle):
            
            if int(gpio.input(12)) != int(buttonBR):
                buttonBR = int(gpio.input(12))
                counterBR += 1
                
            if int(gpio.input(7)) != int(buttonFL):
                buttonFL = int(gpio.input(7))
                counterFL += 1

        #currAngle+offset >= goalAngle and currAngle-offset <= goalAngle:
        pwm1.stop()
        pwm2.stop()
        self.clearPins()


    def pivotleft(self, angle):
        print('[INFO] Turning left...')
        self.setupPins()
        offset = 2 #degrees
        counterBR = np.uint64(0)
        counterFL = np.uint64(0)

        buttonBR = int(0)
        buttonFL = int(0)

        # Initialize pwm signal to control motor
        pwm1 = gpio.PWM(33, 50) #Right side
        pwm2 = gpio.PWM(37, 50) #Left side
        val = 55
        pwm1.start(val)
        pwm2.start(val)
        time.sleep(0.1)
        
        goalAngle = (self.getIMUReading() + angle)%360

        while (self.getIMUReading()+offset <= goalAngle and self.getIMUReading()-offset >= goalAngle):
            
            if int(gpio.input(12)) != int(buttonBR):
                buttonBR = int(gpio.input(12))
                counterBR += 1
                
            if int(gpio.input(7)) != int(buttonFL):
                buttonFL = int(gpio.input(7))
                counterFL += 1

        #if currAngle+offset >= goalAngle and currAngle-offset <= goalAngle:
        pwm1.stop()
        pwm2.stop()
        self.clearPins()
        #break
        
    def orientLeft(self, angle):
        print('[INFO] Orient left...')
        self.setupPins()
        offset = 0.5 #degrees

        goalAngle = (self.getIMUReading() + angle)%360
        # Initialize pwm signal to control motor
        pwm1 = gpio.PWM(33, 50) #Right side
        pwm2 = gpio.PWM(37, 50) #Left side
        val = 55
        
        while True:
            pwm1.start(val)
            pwm2.start(val)
            
            time.sleep(0.01)
            
            pwm1.stop()
            pwm2.stop()
            
            if (self.getIMUReading()+offset >= goalAngle and self.getIMUReading()-offset <= goalAngle):
                self.clearPins()
                break
            else:
                continue
            
            
    def orientRight(self, angle):
        print('[INFO] Orient right...')
        self.setupPins()
        offset = 0.5 #degrees

        goalAngle = (self.getIMUReading() + angle)%360
        # Initialize pwm signal to control motor
        pwm1 = gpio.PWM(31, 50) #Right side
        pwm2 = gpio.PWM(35, 50) #Left side
        val = 55
        
        while True:
            pwm1.start(val)
            pwm2.start(val)
            
            time.sleep(0.1)
            
            pwm1.stop()
            pwm2.stop()
            
            if (self.getIMUReading()+offset >= goalAngle and self.getIMUReading()-offset <= goalAngle):
                self.clearPins()
                break
            else:
                continue