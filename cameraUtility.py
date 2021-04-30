import cv2
import numpy as np
import imutils
import time
from datetime import datetime
from picamera.array import PiRGBArray
from picamera import PiCamera

#globals
GREEN_THRESHOLD = ((65, 60, 30), (85, 255, 255)) #Green
RED_THRESHOLD = ((150, 70, 50), (180, 255, 255)) #Red
BLUE_THRESHOLD = ((150, 90, 50), (180, 255, 255)) #TO BE FIXED

THRESHOLDS = {"PFIZER":GREEN_THRESHOLD, "MODERNA":RED_THRESHOLD, "J&J": BLUE_THRESHOLD}

class Camera:

    def __init__(self):
        self.image = None
        self.frame = None
        

    def getCurrentImage(self):
        return self.image

    def detectVaccine(self, vaccineName):
        global THRESHOLDS
        
        X = 0
        Y = 0
        radius = 0.0
        #global forwardCount
#         height = (image.shape[0])
#         width = (image.shape[1])
        
        #getting the HSV
        hsvImage = cv2.cvtColor(self.getCurrentImage(), cv2.COLOR_BGR2HSV)
        thres = cv2.inRange(hsvImage, THRESHOLDS[vaccineName][0], THRESHOLDS[vaccineName][1])
        contours, hierarchy = cv2.findContours(thres, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        #print(contours)
        
        #centerX = int(640/2)
        #centerY = int(480/2)
        
        #to print the center of the frame
        #image = cv2.line(image, (centerX-20,centerY), (centerX+20,centerY), (0, 0, 0), 2)
        #image = cv2.line(image, (centerX,centerY-20), (centerX,centerY+20), (0, 0, 0), 2)
        
        if len(contours) == 0:
            return (False, X, Y, radius)
        else:
            c = max(contours, key=cv2.contourArea)
            ((X,Y), radius) = cv2.minEnclosingCircle(c)
            print('can see the object')
            return (True, X, Y, radius)
        
            #image = cv2.circle(image, (int(X),int(Y)), int(radius), (0, 0, 255), 2)
            #image = cv2.circle(image, (int(X),int(Y)), 2, (0, 0, 255), 2)
            #cv2.putText(image, '('+str(X)+','+str(Y)+')', (20, 20),cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), 2)
            
            
            
                
        #return image


    def startCamera(self, _):
        # initialize the Raspberry Pi camera
        #camera = PiCamera()
        #camera.resolution = (640, 480)
        #camera.framerate = 25
        #rawCapture = PiRGBArray(camera, size=(640,480))
        cap = cv2.VideoCapture(0)
        # allow the camera to warmup
        time.sleep(0.1)

        # define the codec and create VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter('CompleteCompetition.avi', fourcc, 10, (640, 480))

        # keep looping
        #for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=False):
        while(cap.isOpened()):
            
            ret, frame = cap.read()
            if ret == True:
                
                image = cv2.rotate(frame, cv2.ROTATE_180)
                self.image = image
                
                #processedImage = detectOBI(image)
                #CURRENTIMAGE = image
                out.write(image)
            
                # show the frame to our screen
                cv2.imshow("Frame", image)
               
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break
        cap.release()
        out.release()
        cv2.destroyAllWindows()
            # clear the stream in preparation for the next frame
            #rawCapture.truncate(0)
            # press the 'q' key to stop the video stream
            #if key == ord("q"):
            #    break
            
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()
        
    def recognizeFace(self):
        time.sleep(2.0)
        # loop over the frames from the video stream
        #while True:
        # grab the frame from the threaded video stream and resize it
        # to have a maximum width of 400 pixels
        frame = self.image
        frame = imutils.resize(frame, width=400)
 
        # grab the frame dimensions and convert it to a blob
        (h, w) = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0,
            (300, 300), (104.0, 177.0, 123.0))
 
        # pass the blob through the network and obtain the detections and predictions
        net.setInput(blob)
        detections = net.forward()

        # loop over the detections
        for i in range(0, detections.shape[2]):
            # extract the confidence (i.e., probability) associated with the prediction
            confidence = detections[0, 0, i, 2]

            # filter out weak detections by ensuring the `confidence` is
            # greater than the minimum confidence
            if confidence < 0.5:
                continue

            # compute the (x, y)-coordinates of the bounding box for the object
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")
 
            # draw the bounding box of the face along with the associated probability
            text = "{:.2f}%".format(confidence * 100)
            y = startY - 10 if startY - 10 > 10 else startY + 10
            cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 255, 0), 2)
            cv2.putText(frame, text, (startX, y), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 2)

            # show the output frame
            #self.out.write(frame)
            
            # show the frame to our screen
            #cv2.imshow("Frame", frame)
            #cv2.imshow("Frame", cv2.flip(frame,-1))
            #key = cv2.waitKey(1) & 0xFF
 
            # if the `q` key was pressed, break from the loop
            #if key == ord("q"):
            #    break

            #cv2.destroyAllWindows()

    def detectQRCode(self):
        #define detector
        detector = cv2.QRCodeDetector()

        while True:
            #check, img = cap.read() #check is a bool
            print('[INFO] Looking for QR Code...')
            img = self.getCurrentImage()
            data, bbox, _ = detector.detectAndDecode(img)
            if(bbox is not None):
                for i in range(len(bbox)):
                    cv2.line(img, tuple(bbox[i][0]), tuple(bbox[(i+1) % len(bbox)][0]), color = (0,0,255), thickness = 4)
                    cv2.putText(img, data, (int(bbox[0][0][0]), int(bbox[0][0][1])-10),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                    cv2.imwrite("QRCodeImage.jpg", img)
            if data:
                return data
                break

            #show result to screen
            #cv2.imshow("QR Code detector",img)
