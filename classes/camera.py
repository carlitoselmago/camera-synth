from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import numpy as np
import cv2

from classes.socketserver import socketServer
import time
import random
import threading
import sys
import json



class Camera():

	last_people=0
	wmode=False

	detector="hog"#"edge"#"hog"

	def __init__(self,arg):
		try:
			if arg[1]=="window":
				print("opening in window mode")
				self.wmode=True
		except:
			pass

		self.SS=socketServer()
		self.SS.startSession()

		width=440#160*2#640#320
		height=280#160#480#240

		# initialize the camera and grab a reference to the raw camera capture
		camera = PiCamera()
		camera.resolution = (width, height)
		camera.framerate = 15
		camera.rotation = 0#180

		rawCapture = PiRGBArray(camera, size=(width, height))


		# allow the camera to warmup
		time.sleep(0.1)

		if self.detector=="edge":
			from classes.edge import peopleDetector
			PD=peopleDetector()

		else:
			hog = cv2.HOGDescriptor()
			hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())



		# capture frames from the camera
		for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):

			image = frame.array
			#image = cv2.flip(image, 0)
			#image=cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
			#image = cv2.flip(image, 1)
			#image = cv2.flip(image, 0)

			boxes=[]

			if self.detector=="edge":
				boxes=PD.getPeople(image)
			else:
				gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
				boxes, weights = hog.detectMultiScale(gray, winStride=(2,2),hitThreshold=0.01)#,minSize=(20,20) )
				boxes = np.array([[x, y, x + w, y + h] for (x, y, w, h) in boxes])

			people=len(boxes)
			#print("people",len(boxes))
			#oscSender.send_message('/peoplecount',people)
			"""
			if people>self.last_people:
				print("morepeople")
				self.SS.sendMessage("morepeople")
				#oscSender.send_message('/morepeople',people-last_people)

			if people<self.last_people:
				print("less people")
				self.SS.sendMessage("lesspeople")
				#oscSender.send_message('/lesspeople',last_people-people)
			"""

			if len(boxes)>0:

				centers=[]
				for (xA, yA, xB, yB) in boxes:
					coord=[xA,yA,(xB-xA),(yB-yA)]
					centerCoord = (int(coord[0]+(coord[2]/2)), int(coord[1]+(coord[3]/2)))
					centers.append(centerCoord)
					if self.wmode:
						# display the detected boxes in the colour picture
						#cv2.rectangle(image, (centerCoord[0]-5, centerCoord[1]-5), (centerCoord[0]+5, centerCoord[1]+5),(0, 255, 0), 2)
						cv2.rectangle(image, (xA, yA), (xB, yB),(0, 255, 0), 2)

				#send data
				self.SS.sendMessage(json.dumps(centers))

			if self.wmode:
				cv2.imshow("Frame", image);
			key = cv2.waitKey(1) & 0xFF
			rawCapture.truncate(0)

			if key == ord("q"):
			   break
			self.last_people=people
