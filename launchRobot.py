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



def readCameraImage(Camera01):    
    while True:
        time.sleep(0.1)
        currentImage = Camera01.getCurrentImage()
#         print('in here')
        if isinstance(currentImage, np.ndarray):
            #Camera01.recognizeFace()
            #print(CNTRL.getIMUReading())
            #print(CNTRL.getDistance())
            print("Got Image")
            #cv2.imshow("Frame", CURRENTIMAGE)    
            

def startCompetetion():
    try:
        if EMAIL.checkStartEmail() == True:
            
            Camera01 = CMRA.Camera()
            cameraThread = Thread(target = Camera01.startCamera, args = (Camera01,))
            #cameraThread.daemon = True
            cameraThread.start()
            
            IMUThread = Thread(target = CNTRL.IMUReading)
            IMUThread.daemon = True
            IMUThread.start()
            
            DistanceThread = Thread(target = CNTRL.distanceReading)
            DistanceThread.daemon = True
            DistanceThread.start()
            
            readImageThread = Thread(target = readCameraImage)
            readImageThread.daemon = True
            readImageThread.start()
            
            while True:
                if key == ord("q"):
                    sys.exit()
                    break

    except Exception as e: print(e)
            #print("Failed to start the Competetion.")




if __name__ == "__main__":
    startCompetetion()