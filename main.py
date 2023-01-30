from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import numpy as np
import cv2

from pythonosc import udp_client
from pythonosc import osc_message_builder
import time
import random

last_people=0

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
camera.rotation = 180

rawCapture = PiRGBArray(camera, size=(640, 480))
# allow the camera to warmup
time.sleep(0.1)
hog = cv2.HOGDescriptor()	
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

oscSender = udp_client.SimpleUDPClient("192.168.1.133", 8000)

# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):

    image = frame.array
    image = cv2.flip(image, 0)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    boxes, weights = hog.detectMultiScale(gray, winStride=(8,8) )
    boxes = np.array([[x, y, x + w, y + h] for (x, y, w, h) in boxes])
    
    people=len(boxes)
    print("people",len(boxes))
    #oscSender.send_message('/peoplecount',people)
    
    if people>last_people:
        print("morepeople")
        oscSender.send_message('/morepeople',people-last_people)
		
    if people<last_people:
        print("less people")
        oscSender.send_message('/lesspeople',last_people-people)
    
    for (xA, yA, xB, yB) in boxes:
        # display the detected boxes in the colour picture
        cv2.rectangle(image, (xA, yA), (xB, yB),(0, 255, 0), 2)
    cv2.imshow("Frame", image);
    key = cv2.waitKey(1) & 0xFF
    rawCapture.truncate(0)
    if key == ord("q"):
       break
    last_people=people
