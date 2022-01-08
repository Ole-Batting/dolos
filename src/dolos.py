
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
            print('\nold_hash == new_hash', load_frame)
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
        print(f'\nStarting animation named {name}')

        filepath = f"output/{name}.{self.config['video']['ext']}"
        size = tuple(self.config['dimensions']['resolution'])
        fps = self.config['video']['fps']
        chps = self.config['video']['chps']
        n = fps // chps
        m = len(lines)

        print(f'\nAnimating {m} lines of code\n')

        fourcc = cv2.VideoWriter_fourcc(*self.config['video']['fourcc'])
        writer = cv2.VideoWriter(filepath, fourcc, fps, size)
        self._add_frames(self.frame, writer, n)

        print(f' -- 0/{m} lines animated -- ', end = '\r')

        for row, [line, tabs] in enumerate(lines):
            row_frame = self.frame.copy()
            row_typewriter = Typewriter(self.config, row_frame)
            row_typewriter.active_line(row)
            self._add_frames(row_typewriter.image, writer, n)
            for i in range(len(line)):
                row_typewriter.add_line(line[:i + 1], row, tabs)
                self._add_frames(row_typewriter.image, writer, n)
            self.frame = self.typewriter.add_line(line, row, tabs)
            print(f' -- {row + 1}/{m} lines animated -- ', end = '\r')
        writer.release()

        print(f' -- {m}/{m} lines animated -- \n -- done -- \n')

if __name__ == '__main__':
    anim = Animator()
    anim.animate([
        ["class Guitar", 0],
        ["def __init__(self):", 1],
        ["self.tone_dict = {", 2],
        ["'C': 0, 'C#': 1,", 3],
        ["'Db': 1, 'D': 2, 'D#': 3,", 3],
        ["'Eb': 3, 'E': 4,", 3],
        ["'F': 5, 'F#': 6,", 3],
        ["'Gb': 6, 'G': 7, 'G#': 8,", 3],
        ["'Ab': 8, 'A': 9, 'A#': 10,", 3],
        ["'Bb': 10, 'B': 11", 3],
        ["}", 2],
        ["", 2],
        ["self.note_dict = {", 2],
        ["'M': ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B'],", 3],
        ["'m': ['C','Db','D','Eb','E','F','Gb','G','Ab','A','Bb','B']", 3],
        ["}", 2],
        ["", 2],
        ["self.chord_base_dict = {", 2],
        ["'M': np.array([0,4,7]),", 3],
        ["'M7': np.array([0,4,7,11]),", 3],
        ["'maj7': np.array([0,4,7,11]),", 3],
        ["'m': np.array([0,3,7]),", 3],
        ["'m7': np.array([0,3,7,10]),", 3],
        ["'dim': np.array([0,3,6]),", 3],
        ["'dim7': np.array([0,3,6,9]),", 3],
        ["'aug': np.array([0,4,8]),", 3],
        ["'aug7': np.array([0,4,8,11]),", 3],
        ["'7': np.array([0,4,7,10]),", 3],
        ["'mM7': np.array([0,3,7,11])", 3],
        ["}", 2]
    ], 'testvid')
