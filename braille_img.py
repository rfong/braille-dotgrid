import json
import numpy as np
from optparse import OptionParser
from PIL import Image
import re
import string
from typedecorator import params, returns, setup_typecheck


# https://www.pharmabraille.com/pharmaceutical-braille/the-braille-alphabet/

# Maps "[0-9]" string char up in ASCII space to [a-j]
@returns(str)
@params(c=str)
# `c` must be in [0-9]
def numeral_to_character(c):
    assert len(c)==1
    assert 0 <= int(c) <= 9
    return chr(ord(c) + ord('a') - ord('0'))

@returns(np.ndarray)
@params(arr=np.ndarray)
def interleave_rows_with_zeros(arr):
    '''Interleave a 2D numpy array with zeroed rows.'''
    return np.hstack([arr, np.zeros_like(arr)]).reshape(
        arr.shape[0]*2, arr.shape[1])

@returns(np.ndarray)
@params(grid=np.ndarray, spacing=int)
def dotgrid_to_pixels(grid, spacing=1):
    '''
    Adds empty padding to dotgrid. `spacing` represents how many dots' width
    of padding will go between each dot of information.
    '''
    # Interleave rows, transpose to interleave columns-as-rows, transpose back
    grid = interleave_rows_with_zeros(
        interleave_rows_with_zeros(grid).transpose()
    ).transpose()
    # Now chop off the last row and col, which are empty
    return grid[0:-1, 0:-1]

@returns(np.ndarray)
@params(grid=np.ndarray, margin=int)
def add_margin(grid, margin=1):
    empty_row = np.zeros((margin, grid.shape[1]))
    grid = np.vstack([empty_row, grid, empty_row])
    empty_col = np.zeros((grid.shape[0], margin))
    grid = np.hstack([empty_col, grid, empty_col])
    return grid


class BrailleImageGenerator:

    # str mapping to 2x3 grid representations of braille chars.
    #  1=dot, 0=empty
    braille = None

    def __init__(self):
        # Load braille alphabet from json
        if self.braille == None:
            self.braille = json.loads(open("braille.json","r").read())

    @staticmethod
    def normalize(text):
        '''Normalize for multi-Braille-character string characters'''
        #chr(ord(ch) + ord('a') - ord('0'))

        # Braille "[0-9]" translates up in ASCII space to "#[a-j]".
        # The lambda extracts captures and translates group \1.
        text = re.sub('([0-9]+)',
            lambda match: "#" + ''.join(numeral_to_character(c) for c in match.group(1)),
            text,
        )
        return text

    @returns([np.ndarray])
    @params(self=object, text=str)
    def text_to_braille(self, text):
        '''Translates text into braille chars represented as 2x3 numpy arrays'''
        text = text.lower()
        return [np.array(self.braille[ch]) for ch in text]

    @returns(np.ndarray)
    @params(self=object, brs=[np.ndarray], width=int)
    def braille_to_dotgrid(self, brs, width=10):
        '''
        Wraps braille chars into a dot grid.
        :param brs: a list of 2x3 numpy arrays each representing a braille char
        :param width: the width, in braille chars, of the grid output
        :returns: 2D numpy array
        '''
        # Pad to fully wrap to grid
        mod = len(brs)%width
        if mod != 0:
            brs += [np.array(self.braille[' '])] * (width-mod)
        # Wrap and stack together (sorry I love list comprehensions so much)
        return np.vstack(tuple([
            np.hstack(brs[row_index*width:(row_index+1)*width])
            for row_index in xrange(len(brs)/width)
        ]))

    #def interleave(a, b):
    #    '''interleave two 1D numpy arrays'''
    #    return np.vstack((a,b)).reshape((-1,), order='F')

    @returns(Image.Image)
    @params(self=object, text=str, char_width=int, dot_margin=int)
    def convert(self, text, char_width=10, dot_margin=1):
        '''Convert text to a braille representation on a wrapped spaced grid'''
        pixels = dotgrid_to_pixels(
            self.braille_to_dotgrid(
                self.text_to_braille(text), width=char_width))
        pixels = add_margin(pixels, dot_margin)
        return Image.fromarray(pixels.astype('uint8')*255)
    #im = im.convert('L')
    #im = ImageOps.invert(im)
    #im = im.convert('1')


def main():
    parser = OptionParser(usage="usage: %prog [options] inputtext")
    parser.add_option("-o", "--output", dest="output", type=str,
                      help="output file path")
    parser.add_option("--show", dest="show", action="store_true",
                      help="show image (defaults to true if no output file specified)")
    parser.add_option("--width", dest="width", type=int, default=10,
                      help="grid width in braille characters")
    parser.add_option("--margin", dest="margin", type=int, default=1,
                      help="margin in dots")
    parser.add_option("--dotsize", dest="dot_size", type=int, default=10,
                      help="dot size in pixels")
    (options, args) = parser.parse_args()
    assert len(args)==1, "input text required"

    setup_typecheck()
    gen = BrailleImageGenerator()

    im = gen.convert(args[0], char_width=options.width, dot_margin=options.margin)
    im = im.resize((im.size[0]*options.dot_size, im.size[1]*options.dot_size))
    if options.output:
        im.save(options.output)
    if options.show or not options.output:
        im.show()


if __name__ == "__main__":
    main()
