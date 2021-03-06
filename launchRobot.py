#Created by Patan Sanaulla Khan
#Course 809T Building an Autonomous Robot

import emailUtility as EMAIL 
import controlUtility as CNTRL 
import cameraUtility as CMRA
import mappingUtility as MAP
import planner as PLNR
import cv2
import time
from threading import Thread
import numpy as np
import sys
import math

#Global Variables
Camera01 = None
Controls01 = None

def Competetion():
    global Camera01, Controls01
    vaccinesTransported = 0
    vaccineGripped = False
    vaccineDelivered = False
    vaccineType = ''
    
    while vaccinesTransported != 3:
        if not isinstance(Camera01.getCurrentImage(), np.ndarray):
            continue
        
        try:
            if vaccineGripped == False:
                vaccineType = Camera01.detectQRCode()
                EMAIL.sendEmail('QRCodeImage')
                print('[INFO] Request for '+ vaccineType + ' vial!')
            
                while not vaccineGripped:
                    (isVisible, X, Y, radius) = Camera01.detectVaccine(vaccineType)
                    #print(isVisible)
                    if isVisible:
                        vaccineGripped = Controls01.locateVaccine(X, Y, radius)
                    else:
                        print("[INFO] Can't Find the Vial!")
                        Controls01.pivotleft(15)
                
                if vaccineGripped:
                    #GripperClose = Thread(target = Controls01.keepGripperClosed, args = (Controls01, ))
                    #GripperClose.daemon = True
                    #GripperClose.start()
                    
                    cv2.imwrite("VaccineGripped.jpg",Camera01.getCurrentImage())
                    EMAIL.sendEmail('VaccineGripped')
                    #time.sleep(1)
                    Controls01.reverse(20)
                    #time.sleep(0.5)
                    Controls01.orientRight(0)
                    
                    #arrowFound = False
                    #while not arrowFound:
                    #    print('[INFO] Looking for Arrow!')
                    #    (arrowFound, arrowDirection)= Camera01.detectArrow()
                    #    Controls01.orientRight(15)
                    #EMAIL.sendEmail('ArrowImage')
                    #print(arrowDirection)
                    
                
                while vaccineGripped == True and vaccineDelivered == False:
                    #code to move ahead
                    #start point([45,15])
                    AstarPlanner = PLNR.Planner([0,50], [55, 75])
                    steps = AstarPlanner.initiatePlanning()
                    print(steps)
                    
                    X = 15
                    Y = 50
                    prevAngle = Controls01.getIMUReading()
                    for index in range(4, len(steps), 4):
                        X_ = steps[index][0]
                        Y_ = steps[index][0]
                        
                        try:
                            angle = np.rad2deg(math.atan((Y-Y_)/(X-X_)))
                        except ZeroDivisionError:
                            angle = 90
                        #angle = (angle)%360 # as per map
                        print(angle)
                        if angle != prevAngle:
                            if angle >= 180:
                                Controls01.orientLeft(angle)
                            else:
                                Controls01.orientRight(360-angle)
                            prevAngle = angle
                            
                        distance = int(math.sqrt(math.pow((X-X_),2)+math.pow((Y-Y_),2)))
                        Controls01.forward(distance, True)
                        
                        X = X_
                        Y = Y_
                        
                    Controls01.reverse(5)
                    #time.sleep(0.5)
                    Controls01.orientRight(0)
                    personFound = Camera01.recognizeFace()
                    if personFound:
                        Controls01.openGripper()
                        EMAIL.sendEmail('FaceRecognitionImage')
                        vaccineDelivered = True
                        print("[INFO] Vaccine Delivered!")
                        
                MAP.startPlotting() 
                #EMAIL.sendEmail('TrajectoryMap')
                vaccinesTransported += 1
                #sys.exit()
                
        except Exception as e:
            print(e)
            sys.exit()
            

def startCompetetion():
    global Camera01, Controls01
    try:
        #if EMAIL.checkStartEmail() == True:
        if True:
            
            Camera01 = CMRA.Camera()
            cameraThread = Thread(target = Camera01.startCamera, args = (Camera01,))
            #cameraThread.daemon = True
            cameraThread.start()
            
            Controls01 = CNTRL.Controls()
            IMUThread = Thread(target = Controls01.IMUReading, args = (Controls01, ))
            IMUThread.daemon = True
            IMUThread.start()
            
            DistanceThread = Thread(target = Controls01.distanceReading, args = (Controls01, ))
            DistanceThread.daemon = True
            DistanceThread.start()
            
            DeliverVaccines = Thread(target = Competetion)
            DeliverVaccines.start()

                
    except Exception as e: print(e)
            #print("Failed to start the Competetion.")




if __name__ == "__main__":
    startCompetetion()