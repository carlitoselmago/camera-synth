#!/usr/bin/env python

import os
from picamera import PiCamera
from picamera.array import PiRGBArray

import cv2
import os
import sys, getopt
import signal
import time
from edge_impulse_linux.image import ImageImpulseRunner

runner = None

def now():
    return round(time.time() * 1000)


def sigint_handler(sig, frame):
    print('Interrupted')
    if (runner):
        runner.stop()
    sys.exit(0)

signal.signal(signal.SIGINT, sigint_handler)

def help():
    print('python classify.py <path_to_model.eim> <Camera port ID, only required when more than 1 camera is present>')

def main(argv):


    model = "classes/modelfile.eim"

    dir_path = os.path.dirname(os.path.realpath(__file__))
    modelfile = os.path.join(dir_path, model)

    print('MODEL: ' + modelfile)

    with ImageImpulseRunner(modelfile) as runner:
        #try:
        model_info = runner.init()
        print('Loaded runner for "' + model_info['project']['owner'] + ' / ' + model_info['project']['name'] + '"')
        labels = model_info['model_parameters']['labels']

        width=640
        height=480

        # initialize the camera and grab a reference to the raw camera capture
        camera = PiCamera()
        camera.resolution = (width, height)
        camera.framerate = 15
        camera.rotation = 0#180

        rawCapture = PiRGBArray(camera, size=(width, height))

        next_frame = 0 # limit to ~10 fps here

        for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
            #for img in PiRGBArray(camera, size=(width, height)):
            img = frame.array

            print(img.shape)

            if (next_frame > now()):
                time.sleep((next_frame - now()) / 1000)

            # make two cuts from the image, one on the left and one on the right
            features_l, cropped_l = runner.get_features_from_image(img, 'left')
            features_r, cropped_r = runner.get_features_from_image(img, 'right')

            # classify both
            res_l = runner.classify(features_l)
            res_r = runner.classify(features_r)

            cv2.imwrite('debug_l.jpg', cv2.cvtColor(cropped_l, cv2.COLOR_RGB2BGR))
            cv2.imwrite('debug_r.jpg', cv2.cvtColor(cropped_r, cv2.COLOR_RGB2BGR))

            def print_classification(res, tag):
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

            print_classification(res_l, 'LEFT')
            print_classification(res_r, 'RIGHT')

            next_frame = now() + 100
            rawCapture.truncate(0)
        #finally:
        #    if (runner):
        #        runner.stop()

if __name__ == "__main__":
   main(sys.argv[1:])
