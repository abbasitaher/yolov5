import os
from pathlib import Path
from glob import glob
import argparse
import shutil
from tqdm import tqdm
import random

parser = argparse.ArgumentParser()
parser.add_argument('--datasets', type=str, help='path of yolo datasets')
parser.add_argument('--output', type=str, help='path of destination yolo dataset')
args = parser.parse_args()
datasets = args.datasets
dst_dataset = args.output
dst_labels_path = (Path(dst_dataset) / 'labels')
dst_images_path = (Path(dst_dataset) / 'images')
for p in (dst_labels_path, dst_images_path):
    if not p.exists():
        p.mkdir()

dst_dict = {
    'person': '0',
    'car': '1',
    'truck': '2',
    'loader': '2',
    'dozer': '2',
    'pipe' : '3'
    }
flag = True

for d in tqdm(glob(os.path.join(datasets, '*'))):
    obj_names_file = Path(datasets) / d / 'obj.names'
    with open(obj_names_file) as f:
        lines = f.readlines()
    src_dict = {}
    for i, l in enumerate(lines):
        src_dict[str(i)] = l.lower().strip()

    labels_dir = Path(datasets) / d / 'obj_train_data'
    images_dir = Path(datasets) / d / 'images'
    if not labels_dir.exists() or not images_dir.exists():
        continue
     
    for label in glob(os.path.join(labels_dir, '*')):
        image = label.replace('obj_train_data', 'images')[:-4] + '.png'
        with open(label) as f:
            lines = f.readlines()
        label = Path(label)
        label_name = label.parent.parent.name.split('-')[0] + '_' + label.name
        label_path = dst_labels_path / label_name
        with open(label_path, 'w') as f:
            for line in lines:
                new_id = dst_dict[src_dict[line[0]]]
                new_line = new_id + line[1:]
                f.write(new_line)
        image_path = str(label_path).replace('labels', 'images')[:-4] + '.png'
        if Path(image_path).exists():
            print(f'### image already exists: {image_path}')
            continue
        if not Path(image).exists():
            print(f'### image does not exist: {image}')
            continue
        shutil.copyfile(image, image_path)