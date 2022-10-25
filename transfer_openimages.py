import os
import shutil
from glob import glob
from tqdm import tqdm
from pathlib import Path

prefix = "open_images_"
# TODO: Modify with the name of the folder containing the images
IMAGE_DIR = '/media/correct-ai/63DE63766258A981/datasets/Open Images Dataset V6/validation/'
dst = '/home/correct-ai/data/proxeye_yolo/labels/'
img_dst = '/home/correct-ai/data/proxeye_yolo/val/'

images = glob(os.path.join(IMAGE_DIR, '*'))
for img in tqdm(images):
    img_name = Path(img).name
    shutil.copyfile(img, os.path.join(img_dst, prefix + img_name))