
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
	last_frame=np.array([])

	detector="movement"#"edge"#"hog"#"movement"

	cameramode=False

	def __init__(self,arg):
		try:
			if arg[1]=="window":
				print("opening in window mode")
				self.wmode=True
		except:
			pass

		if self.cameramode:
			from picamera.array import PiRGBArray
			from picamera import PiCamera

		self.SS=socketServer()
		self.SS.startSession()

		self.width=440#160*2#640#320
		self.height=280#160#480#240

		if self.cameramode:
			# initialize the camera and grab a reference to the raw camera capture
			camera = PiCamera()
			camera.resolution = (self.width, self.height)
			camera.framerate = 15
			camera.rotation = 0#180
			#exposure etc
			#camera.shutter_speed=1000
			#camera.iso=640

			rawCapture = PiRGBArray(camera, size=(self.width, self.height))
		else:
			rawCapture = cv2.VideoCapture(0)#"azul.mp4")

		# allow the camera to warmup
		time.sleep(0.1)

		if self.detector=="edge":
			from classes.edge import peopleDetector
			PD=peopleDetector()

		if self.detector=="movement":
			from classes.movement import peopleDetector
			PD=peopleDetector(self)
		else:
			hog = cv2.HOGDescriptor()
			hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())


		# capture frames from the camera
		c=0
		skip=3 #this will be used to measure movement variation, too high and won't work, adjust based on cpu lag
		while True:
			frame=self.getframe(rawCapture)
			image=frame.copy()
		
			#image = cv2.flip(image, 0)
			#image=cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
			#image = cv2.flip(image, 1)
			#image = cv2.flip(image, 0)

			boxes=[]

			if self.detector=="edge":
				boxes=PD.getPeople(image)
			if self.detector=="hog":
				gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
				boxes, weights = hog.detectMultiScale(gray, winStride=(2,2),hitThreshold=0.01)#,minSize=(20,20) )
				boxes = np.array([[x, y, x + w, y + h] for (x, y, w, h) in boxes])
				image=gray

			if self.detector=="movement":
				if self.last_frame.any():
					#(B, G, R) = cv2.split(image)
					#gray=cv2.merge([B, B, B])
					#gray=self.adjust_gamma(gray, gamma=0.2)
					#gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

					#print("gray shape",gray.shape)
					boxes=PD.getPeople(image,self.last_frame)
					#image=gray
				else:
					boxes=[]

			#boxes=self.mergeNearbyBoxes(boxes)

			people=len(boxes)

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
				data={"centers":centers,"width":self.width,"height":self.height}
				
				self.SS.sendMessage(json.dumps(data))

			if self.wmode:
				cv2.imshow("Frame", image)
			key = cv2.waitKey(1) & 0xFF
			if self.cameramode:
				rawCapture.truncate(0)

			if key == ord("q"):
				break
			if c==skip:
				self.last_frame=frame
			self.last_people=people
			c+=1
			if c>skip:
				c=0


	def getframe(self,rawCapture):
		if self.cameramode:
			frame= self.camera.capture_continuous(rawCapture, format="bgr", use_video_port=True)
			return frame.array
		else:
			time.sleep(0.06)
			ret, frame = rawCapture.read()
			#frame = imutils.resize(frame, width=self.width,height=self.height)
			#print(frame.shape)
			frame=cv2.resize(frame,(self.width,self.height), interpolation = cv2.INTER_AREA)
			#print("just resized",frame.shape)
			return frame

	def adjust_gamma(self,image, gamma=1.0):
		# build a lookup table mapping the pixel values [0, 255] to
		# their adjusted gamma values
		invGamma = 1.0 / gamma
		table = np.array([((i / 255.0) ** invGamma) * 255
			for i in np.arange(0, 256)]).astype("uint8")
		# apply gamma correction using the lookup table
		return cv2.LUT(image, table)

	
