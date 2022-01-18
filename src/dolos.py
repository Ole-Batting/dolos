
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import cv2
import yaml
import hashlib
import pickle
from dolos_frame import *
from dolos_text import *

class Animator:
    def __init__(self):

        self.config_path = 'src/config/config.yml'
        self.hash_path = 'src/config/config.hash'
        self.frame_path = 'figs/frame.npz'
        self.frame_fig_path = 'figs/frame.png'

        new_hash = hashlib.md5(open(self.config_path, 'rb').read()).hexdigest()
        old_hash = None
        load_frame = None
        if os.path.isfile(self.hash_path):
            old_hash = pickle.load(open(self.hash_path, 'rb'))
            load_frame = old_hash == new_hash
            print('\nold_hash == new_hash', load_frame)
        else:
            load_frame = False

        with open(self.config_path, 'r') as file:
            self.config = yaml.safe_load(file)

        if load_frame and os.path.isfile(self.frame_path):
            self.frame = pickle.load(open(self.frame_path, 'rb'))
        else:
            self.frame = make_frame(self.config)
            plt.imsave(self.frame_fig_path, self.frame.astype(np.uint8))
            pickle.dump(self.frame, open(self.frame_path, 'wb'))
            pickle.dump(new_hash, open(self.hash_path, 'wb'))

        self.typewriter = Typewriter(self.config, self.frame)

    def _reload_frame(self):
        self.frame = pickle.load(open(self.frame_path, 'rb'))
        self.typewriter = Typewriter(self.config, self.frame)

    def _add_frames(self, frame, writer, n):
        for _ in range(n):
            writer.write(frame[:,:,::-1])

    def animate(self, name):
        with open(f'src/jobs/{name}.txt', 'r') as f:
            job = f.readlines()
        cmd = job[0].replace('\n', '')
        lines = [j.replace('\n', '') for j in job[1:]]
        self._animate(lines, name, cmd)
        self._reload_frame()

    def _file_path(self, name):
        size = f"{self.config['dimensions']['resolution']}"
        size = size.replace(', ', 'x').replace('[', '').replace(']', '')
        fps = self.config['video']['fps']
        chps = self.config['video']['chps']
        ext = self.config['video']['ext']
        filepath = f"vids/{name}-{size}px-{fps}fps-{chps}chps.{ext}"
        return filepath

    def _animate(self, lines, name, cmd):
        print(f'\nStarting animation named {name}')

        size = tuple(self.config['dimensions']['resolution'])
        fps = self.config['video']['fps']
        chps = self.config['video']['chps']
        filepath = self._file_path(name)
        n = fps // chps
        m = len(lines)

        print(f'\nAnimating {m} lines of code\n')

        fourcc = cv2.VideoWriter_fourcc(*self.config['video']['fourcc'])
        writer = cv2.VideoWriter(filepath, fourcc, fps, size)

        if cmd=='!STD':
            self._std_animate(lines, writer, n, m)
        elif cmd=='!INS':
            self._ins_animate(lines, writer, n, m)
        writer.release()

        print(f' -- {m}/{m} lines animated -- \n -- done -- \n')
        print(filepath, '\n')
    
    def _std_animate(self, lines, writer, n, m):

        self._add_frames(self.frame, writer, n)
        print(f' -- 0/{m} lines animated -- ', end = '\r')

        for row, rline in enumerate(lines):
            line, tabs = split_tabs(rline)
            row_frame = self.frame.copy()
            row_typewriter = Typewriter(self.config, row_frame)
            row_typewriter.active_line(row)
            self._add_frames(row_typewriter.image, writer, n)
            for i in range(len(line)):
                row_typewriter.add_line(line[:i + 1], row, tabs)
                self._add_frames(row_typewriter.image, writer, n)
            self.frame = self.typewriter.add_line(line, row, tabs)
            print(f' -- {row + 1}/{m} lines animated -- ', end = '\r')

    def _ins_animate(self, lines, writer, n, m):
        m = 0
        for row, rline in enumerate(lines):
            iline, tabs = split_tabs(rline)
            if len(iline)>0 and iline[0]=='^':
                m += 1
            else:
                self.frame = self.typewriter.add_line(iline, row, tabs)
        
        self._add_frames(self.frame, writer, n)
        print(f' -- 0/{m} lines animated -- ', end = '\r')

        for row, rline in enumerate(lines):
            iline, tabs = split_tabs(rline)
            if len(iline)>0 and iline[0]=='^':
                line = iline[1:]
                row_frame = self.frame.copy()
                row_typewriter = Typewriter(self.config, row_frame)
                row_typewriter.active_line(row)
                self._add_frames(row_typewriter.image, writer, n)
                for i in range(len(line)):
                    row_typewriter.add_line(line[:i + 1], row, tabs)
                    self._add_frames(row_typewriter.image, writer, n)
                self.frame = self.typewriter.add_line(line, row, tabs)
                print(f' -- {row + 1}/{m} lines animated -- ', end = '\r')


if __name__ == '__main__':
    anim = Animator()
    jobs_dir = os.listdir('src/jobs')
    jobs_names = [j.replace('.txt', '') for j in jobs_dir]
    vids_dir = os.listdir('vids')
    vids_names = [(v.split('-'))[0] for v in vids_dir]
    if sys.argv[1] == '-all':
        for job in jobs_names:
            anim.animate(job)
    elif sys.argv[1] =='-new':
        for job in jobs_names:
            if job not in vids_names:
                anim.animate(job)
    else:
        for job in sys.argv[1:]:
            anim.animate(job)
