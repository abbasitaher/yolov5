#!/usr/bin/python3
import os
import time
import datetime
import argparse
from glob import glob
import cv2
import numpy as np
import jetson.inference
import jetson.utils
import recorder

parser = argparse.ArgumentParser(description="Test Models")

parser.add_argument("--model", type=str, help='trained model')
parser.add_argument("--labels", type=str, )
parser.add_argument("--input", type=str)
parser.add_argument("--output_dir", type=str)
parser.add_argument("--output_type", type=str, default='video', help='it should be of either video or image sequence.')

args = parser.parse_args()

input = args.input
output_dir = args.output_dir
output_type = args.output_type
labels = args.labels
model = args.model

class Detector():
    '''This class is used for testing trained models.
    '''

    def __init__(self, model, labels, input,
                 output_dir, output_type='video', 
                 skip_empty_images=False) -> None:
        self.net = jetson.inference.detectNet(argv=['--model='+model, '--labels='+labels,
                                '--input-blob=input_0', '--output-cvg=scores', '--output-bbox=boxes'
                                ])
        '''
            Args:
                -model: path of the model which is used for test.
                -labels: path of a text file which labels are stored in.
                -input: either a directory containing images or a video file.
                -output_dir: the output is saved in this direcotry.
                -output_type: either 'video' or 'image sequence'.
                -skip_empty_images: if true, only saves the images which contain detection.
        '''
        self.input = input
        self.labels = labels
        self.thresholds = {
                            'vehicle': 0.35,
                            }
        self.class_dict_coco = {
                            'person': 1,
                            'car': 2,
                            'motorcycle': 2,
                            'bicycle': 2,
                            'bus': 2,
                            'truck': 2,
                            'train': 2
                            }
        with open('./category_table.txt', 'r') as f:
            ctx = f.read()
        self.coco_categories = ctx.split('\n')
        self.class_dict = {
                    0: 'BACKGROUND',
                    1: 'person',
                    2: 'vehicle',
                    }
        self.input_type = self.input_type(input)
        file_name = input.split('/')[-1].split('.')[0] + '_' + model.split('/')[-2] + '.avi' # + '_' +  time.strftime("%Y_%m_%d_%H_%M_%S") 
        file_path = os.path.join(output_dir, file_name)
        self.recorder = recorder.Recorder(output=file_path, frame_size=self.get_image_shape(input))
        self.output_type = output_type
        self.output_dir = output_dir

    def get_image_shape(self, input):
        if self.input_type == 'video':
            cap = cv2.VideoCapture(input)
            success, image = cap.read()
            h, w, _ = image.shape
        else:
            image = cv2.imread(glob(os.path.join(self.input, '*'))[0])
            h, w, _ = image.shape

        return (w, h)


    def input_type(self, input):
        '''Determines the input type.
            Args:
                -input: path of the input.
        '''
        if os.path.isdir(input):
            return 'image sequence'
        elif input.endswith('png') or input.endswith('jpg') or input.endswith('jpeg'):
            return 'image'
        elif input.endswith('avi') or input.endswith('mp4'):
            cap = cv2.VideoCapture(input)
            return 'video'
    
    def run(self):
        print( 'Started at: ', datetime.datetime.now().strftime('%H:%M:%S'))
        if self.input_type == 'image sequence':
            file_names = glob(os.path.join(self.input, '*'))
            file_names = sorted(file_names)
        elif self.input_type == 'video':
            cap = cv2.VideoCapture(self.input)
        counter = 0
        start = time.time()
        whole_time = 0
        while True:
            try:
                if self.input_type == 'image sequence':
                    file = file_names[counter]
                    image = cv2.imread(file)
                elif self.input_type == 'video':
                    success, image = cap.read()
                    if not success:
                        break
            except Exception as e:
                print(e)
            if image is None or image.size == 0:
                print(f'None Image: {file}')
                continue
            image_org = image.copy()
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # run network
            image_cuda = jetson.utils.cudaFromNumpy(image_rgb)
            start = time.time()
            detections = self.net.Detect(image_cuda, overlay='none')
            whole_time += (time.time() - start)
            for d in detections:
                # if d.ClassID != 1:
                #     print(f'{counter} : {d.ClassID}')
                #     print(self.coco_categories[d.ClassID])

                if self.coco_categories[d.ClassID] not in self.class_dict_coco:
                    continue
                d.ClassID = self.class_dict_coco[self.coco_categories[d.ClassID]]
                confidence = '{0:.2f}'.format(d.Confidence)
                # if d.Confidence < 0.3:
                #     continue
                if ((d.Width * d.Height) / (640 * 480)) > 0.8:
                    continue
                if d.Confidence < 0.6 and d.ClassID == 1:
                    continue
                if d.Confidence < 0.6 and d.ClassID == 2:
                    continue
                box=[int(d.Left), int(d.Top), int(d.Left)+int(d.Width), int(d.Top)+int(d.Height)]
                if d.ClassID == 1:
                    color = [0, 0, 255]
                else:
                    color = [255, 0, 0]
                cv2.rectangle(image_org,(box[0],box[1]),(box[2],box[3]),color, 1, cv2.LINE_4)
                cv2.putText(image_org, self.class_dict[d.ClassID] + ',conf=' + confidence,(box[0] - 10, box[1] + 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            if self.output_type == 'video':
                self.recorder.write(image_org)
            elif self.output_type == 'image sequence': 
                if self.input_type == 'image sequence':
                    path, file = os.path.split(file)
                    file = os.path.join(self.output_dir, file)
                elif self.input_type == 'video':
                    file = counter + '.png'
                    file = os.path.join(self.output_dir, file)
                cv2.imwrite(file, image_org)
            counter+=1
            if self.input_type == 'image sequence' and counter == len(file_names):
                break
        print(f'Whole Time: {whole_time}')
        if self.output_type == 'video':
            self.recorder.close()

d = Detector(model=model, labels=labels, input=input, output_dir=output_dir, output_type=output_type)
d.run()
