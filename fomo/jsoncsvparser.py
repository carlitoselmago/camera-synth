import json
from bs4 import BeautifulSoup
import glob
import os

data = []

folder=r"C:\\Users\gamer\Downloads\archive\Train\Train\Annotations\\"


jdata={"version":1, "type": "bounding-box-labels","boundingBoxes": {}}

images=[]

for filename in glob.glob(folder+'*.xml'):

    #filename='image (1).xml'

    with open(filename,"r") as data:
        Bs_data = BeautifulSoup(data, "xml")
        objects=Bs_data.find_all('object')
        head, filename = os.path.split(filename)
        filename=filename.split(".")[0]+".jpg"

        jdata["boundingBoxes"][filename]=[]

        for o in objects:

            name=o.find("name")
            label=name.get_text()
            
            print(label)
            x=o.find('xmin').get_text()
            y=o.find('ymin').get_text()
            width=o.find('xmax').get_text()
            height=o.find('ymax').get_text()
            print(x,y)

            images.append([filename,label,int(x),int(y),int(width),int(height)])
            jdata["boundingBoxes"][filename].append({"label":label,"x":int(x),"y":int(y),"width":int(width),"height":int(height)})



with open('bounding_boxes.labels', 'w') as f:
    json.dump(jdata, f)
