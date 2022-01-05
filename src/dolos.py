
import os
import numpy as np
import matplotlib.pyplot as plt
import cv2
import yaml
import hashlib
import pickle

def add_centered(src: np.array, obj: np.array) -> None:
    src_d = np.array(src.shape)
    obj_d = np.array(obj.shape)
    start = (src_d - obj_d) // 2
    end = start + obj_d
    src[start[0]:end[0], start[1]:end[1]] = obj

def blend_color(c1, ratio, mode):
    if mode == 'mean gray':
        c2 = np.ones((3)) * np.mean(c1)
    elif mode == 'black':
        c2 = np.zeros((3))
    return (ratio * c1 + c2) / (1 + ratio)

def blend_color_palette(c1, ratio, n):
    colors = np.ones((n, 3))
    for i in range(n):
        r = (n - i) / n
        colors[i] = blend_color(c1, ratio / r, 'black')
    return colors

def make_frame(config: dict) -> np.array:
    res = config['dimensions']['resolution']

    bg_color = np.array(config['theme']['background'])
    bg_bands = np.array(config['background']['bgndbands'])

    bk_ratio = config['background']['blockratio']
    bk_size = np.array(config['dimensions']['blocksize'])

    ed_ratio = config['background']['edgeratio']
    ed_bands = config['background']['edgebands']
    ed_width = config['background']['edgewidth']

    # prep additional colors
    bk_color = blend_color(bg_color, bk_ratio, 'mean gray')
    ed_colors = blend_color_palette(bg_color, ed_ratio, ed_bands)

    # make canvas in background color
    frame = np.ones((*np.flip(res), 3)) * bg_color

    # add horizontal lines
    for i in range(bg_bands[0]):
        frame[i::bg_bands[1],:] = ed_colors[-ed_bands // 4]

    # add edge
    for e in range(ed_bands, 0, -1):
        obj = np.ones((*(np.flip(bk_size) + e * ed_width), 3)) * ed_colors[e - 1]
        add_centered(frame, obj)

    # add block
    block = np.ones((*(np.flip(bk_size)), 3)) * bk_color
    add_centered(frame, block)

    return frame

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
        else:
            load_frame = False

        with open(self.config_path, 'r') as file:
            config = yaml.safe_load(file)

        if load_frame and os.path.isfile(self.frame_path):
            self.frame = pickle.load(open(self.frame_path, 'rb'))
        else:
            pickle.dump(new_hash, open(self.hash_path, 'wb'))
            self.frame = make_frame(config)
            plt.imsave(self.frame_fig_path, self.frame.astype(np.uint8))
            pickle.dump(self.frame, open(self.frame_path, 'wb'))

if __name__ == '__main__':
    anim = Animator()
