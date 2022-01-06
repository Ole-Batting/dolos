import numpy as np
from PIL import Image, ImageDraw, ImageFont

def line_splitter(line):
    words = []
    in_string = False
    word = ''
    for i, c in enumerate(line):
        if c in ' .([{}])' and not in_string:
            if word:
                words.append(word)
            words.append(c)
            word = ''
        elif c == "'":
            word += c
            if in_string:
                words.append(word)
                word = ''
                in_string = False
            else:
                in_string = True
        elif c == '#' and not in_string:
            if word:
                words.append(word)
            words.append(line[i:])
            return words
        else:
            word += c
    if word:
        words.append(word)
    return words

def is_numeric(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

class Typewriter:
    def __init__(self, image, config):
        self.cfg = config
        self.image = image
        self.image_pil = Image.fromarray(image)
        self.draw = ImageDraw(self.image_pil)
        self.font = ImageFont(config['font'], config['fontheight'])
        self.res = np.array(config['dimensions']['resolution'])
        self.block = np.array(config['dimensions']['blicksize'])
        self.startx, self.starty = (self.res - self.block) // 2
        self.endx, self.endy = (self.res + self.block) // 2
        self.texth = config['fontheight']
        self.textw = config['fontratio'] * self.texth
        self.lineh = config['lineheight'] * self.texth
        self.textx = self.startx + self.lineh
        self.texty = self.starty + self.lineh
        self.tabw = config['tabwidth']
        self.head = 0

    def add_line(self, *args):
        self._add_line(*args)
        self.image = np.array(self.image_pil)

    def _add_line(self, line, row, tabs):
        x = self.textx + tabs * self.tabw * self.textw
        y = self.texty + row * self.lineh

        words = line_splitter(line)
        for w, word in enumerate(words):
            self.mint(w, word, words, x, y)

    def _write(word, colortag, x, y):
        color = self.cfg['theme'][colortag]
        self.draw((x + self.head * self.textw, y), word, color, font = self.font)
        self.head += len(word)

    def mint(self, w, word, words, x, y):
        color = self.cfg['theme']['regular']
        self.head = 0

        if word in ['def', 'class']:
            self._write(word, 'defclass', x, y)
        elif w - 1 > 0 and words[w - 1] in ['def', 'class']:
            self._write(word, 'construct', x, y)
        elif w + 1 < len(words) and words[w + 1] == '(':
            self._write(word, 'function', x, y)
        elif w - 1 > 0 and word[w - 1] == '.':
            self._write(word, 'member', x, y)
        elif word[0] == "'":
            self._write(word, 'string', x, y)
        elif word[0] == '#':
            self._write(word, 'comment', x, y)
        elif is_numeric(word):
            self._write(word, 'numeric', x, y)
        elif any([c in word for c in '+-*/%<>&|=!']):
            self._write(word, 'operator', x, y)
        elif word == 'self':
            self._write(word, 'self', x, y)
        else:
            self._write(word, 'regular', x, y)
