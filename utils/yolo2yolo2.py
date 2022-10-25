import pandas as pd
import os.path
from tqdm import tqdm
from glob import glob
from pathlib import Path
import shutil
from tqdm import tqdm

# TODO: Modify with the name of the folder containing the images
IMAGE_DIR = '/media/correct-ai/63DE63766258A981/datasets/Open Images Dataset V6/validation/'
dst = '/home/correct-ai/data/proxeye_yolo/val/'
# img_dst = '/home/correct-ai/data/proxeye_yolo/val/'

# Classes tor train (TODO: Modify the names with the desired labels)
# WARNING: first letter should be UPPER case
trainable_classes = ["Car",
                     "Vehicle",
                     "Bus",
                     "Motorcycle",
                     "Jet ski",
                     "Snowmobile",
                     "Truck",
                     "Person",
                     "Boy",
                     "Girl",
                     "Woman",
                     "Man",
                     ]

def SaveBoundingBoxToFile(image_id,label,x_min,x_max,y_min,y_max):
    # Check that the image exist:
    if os.path.isfile(IMAGE_DIR + image_id + '.jpg'):
        # label mapping
        label_index = trainable_codes.index(label)
        if label_index > 6:
            label_index = 0
        elif label_index == 6:
            label_index = 2
        else:
            label_index = 1

        # If the label file exist, append the new bounding box
        file_path = os.path.join(dst, prefix + image_id + ".txt")
        if os.path.isfile(dst + image_id + '.txt'):
            with open(file_path,'a') as f:
                f.write(' '.join([str(label_index),
                                str(round((x_max+x_min)/2,6)),
                                str(round((y_max+y_min)/2,6)),
                                str(round(x_max-x_min,6)),
                                str(round(y_max-y_min,6))])+'\n')
        else:
            with open(file_path,'w') as f:
                f.write(' '.join([str(label_index),
                                str(round((x_max+x_min)/2,6)),
                                str(round((y_max+y_min)/2,6)),
                                str(round(x_max-x_min,6)),
                                str(round(y_max-y_min,6))])+'\n')

if __name__ == '__main__':
    
    # # Get the codes for the trainable classes
    class_descriptions = pd.read_csv('/media/correct-ai/63DE63766258A981/datasets/Open Images Dataset V6/class-descriptions-boxable.csv', names=["class_code","class_name"], header=None)
    prefix = "open_images_"
    trainable_codes = [v[0] for cls in trainable_classes for v in class_descriptions.values if v[1]==cls]
    with open('/media/correct-ai/63DE63766258A981/datasets/Open Images Dataset V6/validation-annotations-bbox.csv') as f:
        lines = f.readlines()
    for l in tqdm(lines[1:]):
        x = l.split(',')
        if x[2] in trainable_codes:
            SaveBoundingBoxToFile(x[0],x[2],float(x[4]),float(x[5]),float(x[6]),float(x[7]))

    # images = glob(os.path.join(IMAGE_DIR, '*'))
    # for img in tqdm(images):
    #     img_name = Path(img).name
    #     shutil.copyfile(img, os.path.join(img_dst, prefix + img_name))