
import os
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
            print('old_hash == new_hash', load_frame)
        else:
            load_frame = False

        with open(self.config_path, 'r') as file:
            self.config = yaml.safe_load(file)

        if load_frame and os.path.isfile(self.frame_path) and False:
            self.frame = pickle.load(open(self.frame_path, 'rb'))
        else:
            pickle.dump(new_hash, open(self.hash_path, 'wb'))
            self.frame = make_frame(self.config)
            plt.imsave(self.frame_fig_path, self.frame.astype(np.uint8))
            pickle.dump(self.frame, open(self.frame_path, 'wb'))

        self.typewriter = Typewriter(self.config, self.frame)

    def _add_frames(self, frame, writer, n):
        for _ in range(n):
            writer.write(frame[:,:,::-1])

    def animate(self, lines, name):
        filepath = f"output/{name}.{self.config['video']['ext']}"
        size = tuple(self.config['dimensions']['resolution'])
        fps = self.config['video']['fps']
        chps = self.config['video']['chps']
        n = fps // chps
        fourcc = cv2.VideoWriter_fourcc(*self.config['video']['fourcc'])
        writer = cv2.VideoWriter(filepath, fourcc, fps, size)
        self._add_frames(self.frame, writer, n)

        for row, [line, tabs] in enumerate(lines):
            row_frame = self.frame.copy()
            row_typewriter = Typewriter(self.config, row_frame)
            row_typewriter.active_line(row)
            self._add_frames(row_typewriter.image, writer, n)
            for i in range(len(line)):
                row_typewriter.add_line(line[:i + 1], row, tabs)
                self._add_frames(row_typewriter.image, writer, n)
            self.frame = self.typewriter.add_line(line, row, tabs)


if __name__ == '__main__':
    anim = Animator()
    anim.animate([
        ['class Guitar', 0],
        ['def __init__(self):', 1]
        
    ], 'testvid')
