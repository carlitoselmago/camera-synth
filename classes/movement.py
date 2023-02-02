import cv2
from classes.helpers import helpers

class peopleDetector():

    #movement detection instead of people

    def __init__(self,camera):
        self.camera=camera
        self.helpers=helpers()
    
    def getPeople(self,frame,prev_frame):

        # find difference between two frames
        diff = cv2.absdiff(prev_frame, frame)

        # convert the frame to grayscale
        diff_gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

        # apply some blur to smoothen the frame
        diff_blur = cv2.GaussianBlur(diff_gray, (15, 15), 0)

        # get the binary image
        _, thresh_bin = cv2.threshold(diff_blur,10, 255, cv2.THRESH_BINARY)
        if self.camera.wmode:
            cv2.imshow("thresh", thresh_bin)
        # find contours
        contours, hierarchy = cv2.findContours(thresh_bin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        bb=[]

        bb=self.helpers.mergeNearbyBoxes(contours)
        #print(bb)
        """
        for contour in contours:
            ca=cv2.contourArea(contour)
            if  ca > 10 and ca < 2000:
                x, y, w, h = cv2.boundingRect(contour)
                bb.append([x, y, x+w, y+h])
        """
        return bb
