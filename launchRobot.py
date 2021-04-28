#Created by Patan Sanaulla KHan
#Course 809T Building an Autonomous Robot


import emailUtility as EMAIL 
import controlUtiltiy as CNTRL 
import cameraUtility as CMRA
from threading import Thread 



def getCameraData:
	#global CURRENTIMAGE
	CURRENTIMAGE = CMRA.CURRENTIMAGE
	print(CURRENTIMAGE)

def startCompetetion():
	try:
		EMAIL.checkStartEmail() == True:

			cameraThread = Thread(target = getCameraData)
			cameraThread.start()

	except:
		print("Failed to start the Competetion.")




if __name__ == "__main__":
	startCompetetion()