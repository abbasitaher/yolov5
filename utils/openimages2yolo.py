import pandas as pd
import os.path
from tqdm import tqdm
from glob import glob
from pathlib import Path
import shutil
from tqdm import tqdm

# TODO: Modify with the name of the folder containing the images

parser = argparse.ArgumentParser()
parser.add_argument('--openimage', type=str, help='path of open image dataset images')
parser.add_argument('--output', type=str, help='path of destination yolo dataset')
args = parser.parse_args()
dst_dataset = args.output
src_dataset = args.openimage
images_src = os.path.join(src_dataset, 'train')
labels_dst = os.path.join(dst_dataset,'labels')
images_dst = os.path.join(dst_dataset,'images')


# Classes tor train (TODO: Modify the names with the desired labels)
# WARNING: first letter should be UPPER case
trainable_classes = ["Car",
                     "Vehicle",
                     "Bus",
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
    if os.path.isfile(os.path.join(images_src, image_id + '.jpg')):
        # label mapping
        label_index = trainable_codes.index(label)
        if label_index in (0, 1, 2, 3):
            label_index = 1
        elif label_index == 4:
            label_index = 2
        elif label_index in (5, 6, 7, 8, 9):
            label_index = 0

        # If the label file exist, append the new bounding box
        file_path = os.path.join(labels_dst, prefix + image_id + ".txt")
        if os.path.isfile(file_path):
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
    dataset_csv = os.path.join(dst_dataset, 'train-annotations-bbox.csv')
    classes_csv = os.path.join(dst_dataset, 'class-descriptions-boxable.csv')
    class_descriptions = pd.read_csv(classes_csv, names=["class_code","class_name"], header=None)
    prefix = "open_images_"
    trainable_codes = [v[0] for cls in trainable_classes for v in class_descriptions.values if v[1]==cls]
    with open(dataset_csv) as f:
        lines = f.readlines()
    for l in tqdm(lines[1:]):
        x = l.split(',')
        if x[2] in trainable_codes:
            SaveBoundingBoxToFile(x[0],x[2],float(x[4]),float(x[5]),float(x[6]),float(x[7]))

    images = glob(os.path.join(images_src, '*'))
    for img in tqdm(images):
        img_name = Path(img).name
        img_dst = os.path.join(images_dst, prefix + img_name)
        if not Path(img_dst).exists():
            shutil.copyfile(img, img_dst)
        