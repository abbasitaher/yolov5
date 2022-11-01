import os
from pathlib import Path
from glob import glob
import argparse
import subprocess


parser = argparse.ArgumentParser()
parser.add_argument('--videos', type=str, help='path of yolo datasets')
parser.add_argument('--datasets', type=str, help='path of destination yolo dataset')
args = parser.parse_args()
yolo_datasets_dir = os.path.join(args.datasets)
yolo_datasets = glob(os.path.join(yolo_datasets_dir, '*'))
yolo_datasets = sorted(yolo_datasets)

for yolo_path in yolo_datasets:
    print ('<<<<<<<<<<<Start>>>>>>>>>>>>')
    if not os.path.isdir(yolo_path):
        print(f'{yolo_path} does not exist.')
        continue
    if yolo_path.endswith('.zip'):
        continue

    dir_name = Path(yolo_path).stem
    if 'prg' in dir_name:
        video_name = dir_name.split('-')[0].upper()
    elif 'weld' in dir_name:
        video_name = dir_name.split('-')[0].lower().replace('task_', '')
    else:
        video_name = dir_name.split('-')[0].replace('rec_data', 'REC_DATA').replace('cam', 'Cam')

    video_path = os.path.join(args.videos, video_name + '.avi')
    print(f'Video Path: {video_path}')
    print(f'Dataset Path: {yolo_path}')
    if not os.path.exists(video_path):
        print(f'{video_path} does not exist.')
        continue
    images_dir = os.path.join(yolo_path, 'images')
    if not os.path.exists(images_dir):
        os.mkdir(images_dir)

    images_format = os.path.join(images_dir, 'frame_%06d.png')
    subprocess.run(['ffmpeg', '-i', video_path, '-start_number', '0', '-b:v', '10000k', '-vsync', '0', '-an', '-y', '-q:v', '16', images_format])
    print ('<<<<<<<<<<<End>>>>>>>>>>>>')

