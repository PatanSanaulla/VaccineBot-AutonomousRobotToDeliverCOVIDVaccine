#Created by Patan Sanaulla Khan
#Course 809T Building an Autonomous Robot

import emailUtility as EMAIL 
import controlUtility as CNTRL 
import cameraUtility as CMRA
import mappingUtility as MAP 
import cv2
import time
from threading import Thread
import numpy as np
import sys

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
                    print(isVisible)
                    if isVisible:
                        vaccineGripped = Controls01.locateVaccine(X, Y, radius)
                    else:
                        print("[INFO] Can't Find the Vial!")
                        Controls01.pivotleft(15)
                
                if vaccineGripped:
                    cv2.imwrite("VaccineGripped.jpg",Camera01.getCurrentImage())
                    EMAIL.sendEmail('VaccineGripped')
                
                while vaccineGripped == True and vaccineDelivered == False:
                    #code to move ahead
                    personFound = Camera01.recognizeFace()
                    if personFound:
                        Controls01.openGripper()
                        EMAIL.sendEmail('FaceRecognitionImage')
                        vaccineDelivered = True
                        print("[INFO] Vaccine Delivered!")
                
                vaccinesTransported += 1
                
        except Exception as e:
            print(e)
            sys.exit()
            #currentImage = Camera01.getCurrentImage()
        #print()
#         print('in here')
        #if isinstance(currentImage, np.ndarray):
            #Camera01.recognizeFace()
            #print(CNTRL.getIMUReading())
            #print(CNTRL.getDistance())
            #print("Got Image")
            #cv2.imshow("Frame", CURRENTIMAGE)    
            

def startCompetetion():
    global Camera01, Controls01
    try:
        if EMAIL.checkStartEmail() == True:
            
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