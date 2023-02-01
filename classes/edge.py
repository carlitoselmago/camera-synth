import cv2
import os
import sys, getopt
import signal
import time
from edge_impulse_linux.image import ImageImpulseRunner

class peopleDetector():

    model = "modelfile.eim"

    def __init__(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        modelfile = os.path.join(dir_path, self.model)

        print('MODEL: ' + modelfile)
        signal.signal(signal.SIGINT, self.sigint_handler)
        self.runner=ImageImpulseRunner(modelfile)

        model_info = self.runner.init()
        #print('Loaded runner for "' + model_info['project']['owner'] + ' / ' + model_info['project']['name'] + '"')
        labels = model_info['model_parameters']['labels']

    def sigint_handler(self,sig, frame):
        print('Interrupted')
        if (self.runner):
            self.runner.stop()
        sys.exit(0)

    def getPeople(self,frame):
        #frame=cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        img = frame

        features_l, cropped_l = self.runner.get_features_from_image(img, 'left')
        features_r, cropped_r = self.runner.get_features_from_image(img, 'right')

        res_l = self.runner.classify(features_l)
        res_r = self.runner.classify(features_r)




        boxes=self.prepareBoxes(res_l)+self.prepareBoxes(res_r,160)




        #self.print_classification(res_l, 'LEFT')
        #self.print_classification(res_r, 'RIGHT')

        return boxes

    def prepareBoxes(self,data,pr=0):
        #pr is Push right, to tranlate right bboxes
        b=[]
        for bb in data["result"]["bounding_boxes"]:
            if  bb['value']>0.91:
                b.append([bb['x']+pr, bb['y'], (bb['x']+pr)+bb['width'], bb['y']+bb['height']])
        return b


    def print_classification(self,res, tag):
        if "classification" in res["result"].keys():
            print('%s: Result (%d ms.) ' % (tag, res['timing']['dsp'] + res['timing']['classification']), end='')
            for label in labels:
                score = res['result']['classification'][label]
                print('%s: %.2f\t' % (label, score), end='')
            print('', flush=True)
        elif "bounding_boxes" in res["result"].keys():
            print('%s: Found %d bounding boxes (%d ms.)' % (tag, len(res["result"]["bounding_boxes"]), res['timing']['dsp'] + res['timing']['classification']))
            for bb in res["result"]["bounding_boxes"]:
                print('\t%s (%.2f): x=%d y=%d w=%d h=%d' % (bb['label'], bb['value'], bb['x'], bb['y'], bb['width'], bb['height']))
