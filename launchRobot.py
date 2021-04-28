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
VACCINESTRANSPORTED = 0
VACCINEGRIPPED = False
VACCINEDELIVERED = False
VACCINETYPE = ''


def Competetion(Camera01, Controls01, _):
	global VACCINESTRANSPORTED

    while VACCINESTRANSPORTED != 3:

    	if VACCINEGRIPPED == False:
    		VACCINETYPE = Camera01.detectQRCode()
    		VACCINEGRIPPED = True

    	if VACCINEGRIPPED == True and VACCINEDELIVERED == False:
    		#code to move ahead
    		print("Reached Here!")


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
            
            Competetion = Thread(target = Competetion, args = (Camera01, Controls01, ))
            Competetion.start()



                
    except Exception as e: print(e)
            #print("Failed to start the Competetion.")




if __name__ == "__main__":
    startCompetetion()