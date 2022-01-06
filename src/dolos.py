
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
