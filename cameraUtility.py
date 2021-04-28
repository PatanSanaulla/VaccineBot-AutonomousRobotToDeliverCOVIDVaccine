import cv2
import numpy as np
import imutils
from datetime import datetime
from picamera.array import PiRGBArray
from picamera import PiCamera

CURRENTIMAGE

def detectOBI(image):
    global forwardCount
    height = (image.shape[0])
    width = (image.shape[1])
    
    #getting the HSV
    hsvImage = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
                     
    #threshold = cv2.inRange(hsvImage, (65, 60, 30), (85, 255, 255)) #Green
    threshold = cv2.inRange(hsvImage, (150, 70, 50), (180, 255, 255)) #Red
    
    contours, hierarchy = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    #print(contours)
    
    centerX = int(640/2)
    centerY = int(480/2)
    
    #to print the center of the frame
    image = cv2.line(image, (centerX-20,centerY), (centerX+20,centerY), (0, 0, 0), 2)
    image = cv2.line(image, (centerX,centerY-20), (centerX,centerY+20), (0, 0, 0), 2)
    
    if len(contours) == 0:
        print('No block found')
    else:
        c = max(contours, key=cv2.contourArea)
        ((X,Y), radius) = cv2.minEnclosingCircle(c)
        image = cv2.circle(image, (int(X),int(Y)), int(radius), (0, 0, 255), 2)
        image = cv2.circle(image, (int(X),int(Y)), 2, (0, 0, 255), 2)
        
        cv2.putText(image, '('+str(X)+','+str(Y)+')', (20, 20),cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), 2)
        degrees = 0
        if(X > 315 and X < 325):
            if radius*2 > 400: #the object is close to the gripper
                closeGripper() #
                pic_time = 'pickedObject'#datetime.now().strftime('%Y%m%d%H%M%S')
                cv2.imwrite(pic_time+'.jpg', image)
                EMAIL.sendEmail(pic_time)
                reverse(forwardCount)
                forwardCount = 0
            else:
                forward(5)
                forwardCount += 5
             #   openGripper()
            return image #within the zone
        
        if(X < centerX):
            #rotate left
            degrees = (320 - X)*0.061
            pivotleft(degrees)
        else:
            #rotate right
            degrees = (640 - X)*0.061
            pivotright(degrees)
            
    return image


def startCamera():
    global CURRENTIMAGE
    # initialize the Raspberry Pi camera
    camera = PiCamera()
    camera.resolution = (640, 480)
    camera.framerate = 25
    rawCapture = PiRGBArray(camera, size=(640,480))

    # allow the camera to warmup
    time.sleep(0.1)

    # define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('trackblockandretrive.avi', fourcc, 10, (640, 480))
    # write frame to video file

    # keep looping
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=False):
        # grab the current frame
        start = datetime.datetime.now()
        
        image = frame.array
        image = cv2.rotate(image, cv2.ROTATE_180)
        
        #processedImage = detectOBI(image)
        CURRENTIMAGE = image
        out.write(processedImage)
        
        # show the frame to our screen
        cv2.imshow("Frame", processedImage)
           
        key = cv2.waitKey(1) & 0xFF
        # clear the stream in preparation for the next frame
        rawCapture.truncate(0)
        # press the 'q' key to stop the video stream
        if key == ord("q"):
            gameover()
            break
        
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()