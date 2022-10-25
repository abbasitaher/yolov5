import subprocess
from pathlib import Path
from datetime import date, datetime, time
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('--root', type=str, default='/home/atefeh/data/videos_for_annotation')

args = parser.parse_args()
root = Path(args.root)

videos_root = root / 'videos'
videos_list = videos_root.glob('*')

duration_root = root / 'durations'
durations_list = duration_root.glob('*')

output_dir = (root / 'shrunk_videos')
output_dir.mkdir(parents=True, exist_ok=True)
time_format = '%H:%M:%S'
for duration_path in durations_list:
    print(f'<<<<<<<<<<<<<<<<<<<<{duration_path}>>>>>>>>>>>>>>>>>>>>>>>>>>>')
    video_path = Path(str(duration_path).replace('durations', 'videos').replace('.txt', '.avi'))

    print(f'<<<<<<<<<<<<<<<<<<<<{video_path}>>>>>>>>>>>>>>>>>>>>>>>>>>>')
    
    if not duration_path.exists():
        continue

    with open(duration_path, mode='r') as f:
        durations = f.readlines()
        for duration in durations:
            if len(duration.strip().split(' - ')) != 2:
                print('>>>>>>>>', duration_path,  duration, 'Format is wrong', sep=' : ')
                continue
            start_time, end_time = duration.replace('\ufeff', '').strip().split(' - ')
            print('start time: ', start_time)
            print('end time: ', end_time)
            duration_time = str(datetime.strptime(end_time, time_format) - datetime.strptime(start_time, time_format))
            output_name = output_dir / (video_path.stem + '_start_' + start_time.replace(':', '') + '_end_' + end_time.replace(':', '') + video_path.suffix)
            subprocess.run(['ffmpeg', '-i', video_path, '-acodec', 'copy', '-vcodec', 'copy', '-ss', start_time, '-t', duration_time, output_name, '-y'])
