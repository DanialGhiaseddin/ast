# -*- coding: utf-8 -*-
# @Time    : 10/19/20 5:15 AM
# @Author  : Yuan Gong
# @Affiliation  : Massachusetts Institute of Technology
# @Email   : yuangong@mit.edu
# @File    : prep_esc50.py

import numpy as np
import json
import os
import zipfile
import wget
import argparse

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("--sample_rate", choices=['16000', '44100'], default='16000', help="Sample Rate")
parser.add_argument("--download_data", default=True)

args = parser.parse_args()


def get_immediate_subdirectories(a_dir):
    return [name for name in os.listdir(a_dir) if os.path.isdir(os.path.join(a_dir, name))]


def get_immediate_files(a_dir):
    return [name for name in os.listdir(a_dir) if os.path.isfile(os.path.join(a_dir, name))]


if not os.path.exists('./data/ESC-50-master'):
    if args.download_data:
        esc50_url = 'https://github.com/karoldvl/ESC-50/archive/master.zip'
        wget.download(esc50_url, out='./data/')
        with zipfile.ZipFile('./data/ESC-50-master.zip', 'r') as zip_ref:
            zip_ref.extractall('./data/')
        os.remove('./data/ESC-50-master.zip')

    # convert the audio to 16kHz
base_dir = './data/ESC-50-master'
if int(args.sample_rate) == 16000:
    if not os.path.exists('./data/ESC-50-master/audio_16k/'):
        os.mkdir('./data/ESC-50-master/audio_16k/')
        audio_list = get_immediate_files('./data/ESC-50-master/audio')
        for audio in audio_list:
            print('sox ' + base_dir + '/audio/' + audio + ' -r 16000 ' + base_dir + '/audio_16k/' + audio)
            os.system('sox ' + base_dir + '/audio/' + audio + ' -r 16000 ' + base_dir + '/audio_16k/' + audio)

label_set = np.loadtxt('./data/esc_class_labels_indices.csv', delimiter=',', dtype='str')
label_map = {}
for i in range(1, len(label_set)):
    label_map[eval(label_set[i][2])] = label_set[i][0]
print(label_map)

# fix bug: generate an empty directory to save json files
if not os.path.exists('./data/datafiles'):
    os.mkdir('./data/datafiles')

for fold in [1, 2, 3, 4, 5]:
    if int(args.sample_rate) == 16000:
        base_path = "./data/ESC-50-master/audio_16k/"
    else:
        base_path = "./data/ESC-50-master/audio/"

    meta = np.loadtxt('./data/ESC-50-master/meta/esc50.csv', delimiter=',', dtype='str', skiprows=1)
    train_wav_list = []
    eval_wav_list = []
    for i in range(0, len(meta)):
        cur_label = label_map[meta[i][3]]
        cur_path = meta[i][0]
        cur_fold = int(meta[i][1])
        if int(cur_label) < 30:
            # /m/07rwj is just a dummy prefix
            cur_dict = {"wav": base_path + cur_path, "labels": '/m/07rwj' + cur_label.zfill(2)}
            if cur_fold == fold:
                eval_wav_list.append(cur_dict)
            else:
                train_wav_list.append(cur_dict)

    print('fold {:d}: {:d} training samples, {:d} test samples'.format(fold, len(train_wav_list), len(eval_wav_list)))

    with open('./data/datafiles/esc_train_data_' + str(fold) + '.json', 'w') as f:
        json.dump({'data': train_wav_list}, f, indent=1)

    with open('./data/datafiles/esc_eval_data_' + str(fold) + '.json', 'w') as f:
        json.dump({'data': eval_wav_list}, f, indent=1)

print('Finished ESC-50 Preparation')
