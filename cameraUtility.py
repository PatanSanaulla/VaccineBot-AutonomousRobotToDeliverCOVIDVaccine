import cv2
import numpy as np
import imutils
import time
from datetime import datetime
from picamera.array import PiRGBArray
from picamera import PiCamera

#globals
GREEN_THRESHOLD = ((65, 60, 30), (85, 255, 255))
RED_THRESHOLD = ((150, 70, 50), (180, 255, 255))
BLUE_THRESHOLD = ((150, 90, 50), (180, 255, 255)) #TO BE FIXED
YELLOW_THRESHOLD = ((5, 40, 135), (60, 255, 255))

#laundry room
#GREEN_THRESHOLD = ((45, 50, 30), (70, 255, 255))
#RED_THRESHOLD = ((120, 60, 30), (255, 255, 255))
#BLUE_THRESHOLD = ((150, 90, 50), (180, 255, 255)) #TO BE FIXED
#YELLOW_THRESHOLD = ((0, 40, 150), (75, 255, 255))



THRESHOLDS = {"PFIZER":RED_THRESHOLD, "MODERNA":GREEN_THRESHOLD, "J&J": BLUE_THRESHOLD}

NEURAL_NET = cv2.dnn.readNetFromCaffe('deploy.prototxt.txt', 'res10_300x300_ssd_iter_140000.caffemodel')

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
        
        #getting the HSV
        hsvImage = cv2.cvtColor(self.getCurrentImage(), cv2.COLOR_BGR2HSV)
        thres = cv2.inRange(hsvImage, THRESHOLDS[vaccineName][0], THRESHOLDS[vaccineName][1])
        contours, hierarchy = cv2.findContours(thres, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
 
        if len(contours) == 0:
            return (False, X, Y, radius)
        else:
            c = max(contours, key=cv2.contourArea)
            ((X,Y), radius) = cv2.minEnclosingCircle(c)
            return (True, X, Y, radius)


    def startCamera(self, _):
        cap = cv2.VideoCapture(0)
        # allow the camera to warmup
        time.sleep(0.1)

        # define the codec and create VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter('CompleteCompetition.avi', fourcc, 10, (640, 480))

        # keep looping
        while(cap.isOpened()):
            
            ret, frame = cap.read()
            if ret == True:
                
                image = cv2.rotate(frame, cv2.ROTATE_180)
                self.image = image
                
                out.write(image)
            
                # show the frame to our screen
                cv2.imshow("Frame", image)
               
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break
        cap.release()
        out.release()
        cv2.destroyAllWindows()

        
    def recognizeFace(self):
        
        print('[INFO] Looking for Person...')
        
        faceNotFound = True
        # loop over the frames from the video stream
        while faceNotFound:
            frame = self.getCurrentImage()
            # grab the frame from the threaded video stream and resize it to have a maximum width of 400 pixels
            frame = imutils.resize(frame, width=400)
 
            # grab the frame dimensions and convert it to a blob
            (h, w) = frame.shape[:2]
            blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0,
                (300, 300), (104.0, 177.0, 123.0))
 
            # pass the blob through the network and obtain the detections and predictions
            NEURAL_NET.setInput(blob)
            detections = NEURAL_NET.forward()

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
                
                cv2.imwrite("FaceRecognitionImage.jpg",frame)
                faceNotFound = False
                break
        
        return True
            

    def detectQRCode(self):
        print('[INFO] Looking for QR Code...')
        #define detector
        detector = cv2.QRCodeDetector()

        while True:
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
            
    def detectArrow(self):
        global YELLOW_THRESHOLD
        arrowDirection = ''
        arrowFound = False
        #getting the HSV
        image = self.getCurrentImage()
        hsvImage = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
        #setting the threshold for the color
        thres = cv2.inRange(hsvImage, YELLOW_THRESHOLD[0], YELLOW_THRESHOLD[1])#Yellow 
    
        GB = cv2.GaussianBlur(thres,(5,5), cv2.BORDER_DEFAULT)
    
        #applying Harris Corner
        #dst = cv2.cornerHarris(GB, 2, 3, 0.04)
        #dst = cv2.dilate(dst, None)
        #image[dst>0.01*dst.max()] = [0, 0, 255]
    
        #applying Shi_tomasi method
        corners = cv2.goodFeaturesToTrack(GB, 7, 0.01, 10)
        try:
            corners = np.int0(corners)
        except:
            #cv2.rectangle(image, (0,0), (255,50), (255, 255, 255), -1)
            #cv2.putText(image, "Orientation: None", (20, 20),cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
            return (arrowFound, arrowDirection)
    
        ((cx,cy), radius) = cv2.minEnclosingCircle(corners)
        image = cv2.circle(image, (int(cx),int(cy)), 2, (0, 0, 255), 2)
        
        if len(corners) >= 5:
            arrowFound = True
    
        x_coord = []
        y_coord = []
        for i in corners:
            x, y = i.ravel()
            x_coord.append(x)
            y_coord.append(y)
            cv2.circle(image, (x,y), 2, (0, 0, 255), 2)
        
        x_diff = abs(max(x_coord) - min(x_coord))
        y_diff = abs(max(y_coord) - min(y_coord))
    
        cv2.rectangle(image, (0,0), (255,50), (255, 255, 255), -1)
        pointsWithin = 0
        if y_diff > x_diff:
            #Can only be "up/Down"

            #to check if lies within up
            y_diff = abs(int(cy)-min(y_coord))
            Area_of_side = x_diff * y_diff
        
            for i in range(0, len(x_coord)):
                Area_sum = (0.5)*(x_diff)*abs(y_coord[i]-int(cy)) + (0.5)*(x_diff)*abs(y_coord[i]-min(y_coord)) + (0.5)*(y_diff)*abs(x_coord[i]-min(x_coord)) + (0.5)*(y_diff)*abs(max(x_coord)-x_coord[i])
    
                if Area_sum <= Area_of_side:
                    pointsWithin = pointsWithin + 1
        
            if pointsWithin > 3:
                cv2.putText(image, "Orientation: UP", (20, 20),cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
            else:
                cv2.putText(image, "Orientation: DOWN", (20, 20),cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
        else:
            #Can only be "left/Right"
        
            #to check if lies within left
            X_diff = abs(int(cx)-min(x_coord))
            Area_of_side = x_diff * y_diff
        
            for i in range(0, len(x_coord)):
                Area_sum = (0.5)*(x_diff)*abs(max(y_coord)-y_coord[i]) + (0.5)*(x_diff)*abs(y_coord[i]-min(y_coord)) + (0.5)*(y_diff)*abs(x_coord[i]-min(x_coord)) + (0.5)*(y_diff)*abs(int(cx)-x_coord[i])
            
                if Area_sum <= Area_of_side:
                    pointsWithin = pointsWithin + 1
        
            if pointsWithin > 3:
                cv2.putText(image, "Orientation: LEFT", (20, 20),cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
                arrowDirection = 'LEFT'
            else:
                cv2.putText(image, "Orientation: RIGHT", (20, 20),cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
                arrowDirection = 'RIGHT'
                
            if arrowFound:
                cv2.imwrite("ArrowImage.jpg", image)
        
        return (arrowFound, arrowDirection)
