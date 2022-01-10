import numpy as np
from PIL import Image, ImageDraw, ImageFont
from dolos_frame import blend_color

def line_splitter(line):
    words = []
    in_string = False
    word = ''
    for i, c in enumerate(line):
        if c in ' .,:-*([{}])' and not in_string:
            if c not in '.-*' or not is_numeric(word):
                if word:
                    words.append(word)
                words.append(c)
                word = ''
            else:
                word += c
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
    def __init__(self, config, image):
        self.cfg = config
        self.image = image
        self.image_pil = Image.fromarray(image)
        self.draw = ImageDraw.Draw(self.image_pil)
        self.font = ImageFont.truetype(config['font'], config['fontheight'])
        self.res = np.array(config['dimensions']['resolution'])
        self.block = np.array(config['dimensions']['blocksize'])
        self.startx, self.starty = (self.res - self.block) // 2
        self.endx, self.endy = (self.res + self.block) // 2
        self.texth = config['fontheight']
        self.textw = config['fontratio'] * self.texth
        self.lineh = config['dimensions']['lineheight'] * self.texth
        self.textx = self.startx + self.lineh
        self.texty = self.starty + self.lineh
        self.tabw = config['tabwidth']
        self.head = 0

        self.statements = [
            'def',
            'class',
            'if',
            'elif',
            'else',
            'import',
            'as',
            'is',
            'in',
            'and',
            'or',
            'return',
            'for',
            'while',
            'from',
            'not',
            'try',
            'except',
            'finally',
            'with',
            'None'
        ]

    def add_line(self, *args):
        self._add_line(*args)
        self.image = np.array(self.image_pil)
        return self.image

    def _add_line(self, line, row, tabs):
        self.head = 0
        x = self.textx + tabs * self.tabw * self.textw
        y = self.texty + row * self.lineh

        words = line_splitter(line)
        for w, word in enumerate(words):
            self.mint(w, word, words, x, y)

    def _write(self, word, colortag, x, y):
        color = tuple(self.cfg['theme'][colortag])
        self.draw.text((x + self.head * self.textw, y), word, color, font = self.font)
        self.head += len(word)

    def mint(self, w, word, words, x, y):
        color = self.cfg['theme']['regular']

        if word in self.statements:
            self._write(word, 'statement', x, y)
        elif w - 2 >= 0 and words[w - 2] in ['def', 'class']:
            self._write(word, 'construct', x, y)
        elif w + 1 < len(words) and words[w + 1] == '(':
            self._write(word, 'function', x, y)
        elif w - 1 >= 0 and words[w - 1] == '.':
            self._write(word, 'member', x, y)
        elif word[0] in ["'", '"'] or word[:2] in ["r'", 'r"', "f'", 'f"']:
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

    def active_line(self, row):
        color = blend_color(np.array(self.cfg['theme']['background']),
                            self.cfg['background']['actratio'],
                            mode = 'white')
        y1 = int(self.texty + row * self.lineh)
        y2 = int(self.texty + (row + 1) * self.lineh)
        try:
            self.image[y1:y2, self.startx:self.endx] = \
                np.ones((int(self.lineh), self.block[0], 3), dtype=np.uint8) * color
        except ValueError:
            print(f"\nErr at row = {row}")
            raise
        self.image_pil = Image.fromarray(self.image)
        self.draw = ImageDraw.Draw(self.image_pil)

if __name__ == '__main__':
    print(line_splitter(' linewidth = 5 if i == 0 and fr == 1 else None)'))
