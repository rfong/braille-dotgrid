import json
import numpy as np
from optparse import OptionParser
from PIL import Image
import re
import string
from typedecorator import params, returns, setup_typecheck


# Maps "[0-9]" string char up in ASCII space to [a-j]
@returns(str)
@params(c=str)
# `c` must be in [0-9]
def numeral_to_character(c):
    assert len(c)==1
    assert 0 <= int(c) <= 9
    return chr(ord(c) + ord('a') - ord('0'))

@returns(np.ndarray)
@params(arr=np.ndarray, zeroed_rows=int)
def interleave_rows_with_zeros(arr, zeroed_rows=1):
    '''Interleave a 2D numpy array with zeroed rows.'''
    return np.hstack([arr] + [np.zeros_like(arr)]*zeroed_rows).reshape(
        arr.shape[0]*(1+zeroed_rows), arr.shape[1])

@returns(np.ndarray)
@params(grid=np.ndarray, padding=int)
def dotgrid_to_pixels(grid, padding=1):
    '''Adds empty padding to dotgrid.'''
    # Interleave rows
    grid = interleave_rows_with_zeros(grid, zeroed_rows=padding)
    # transpose to interleave columns-as-rows, transpose back
    grid = interleave_rows_with_zeros(grid.transpose(), zeroed_rows=padding).transpose()
    # Now chop off the empty outer padding
    return grid[0:-padding, 0:-padding]

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

        # Create alphabet of single characters we know how to handle.
        self.alphabet = "0123456789" + "".join(
            filter(lambda key: len(key) == 1, self.braille.keys()))

    def normalize(self, text):
        '''Normalize for multi-Braille-character string characters'''
        text = text.lower()

        # For now, drop any characters we don't know how to handle.
        filtered_text = filter(self.alphabet.__contains__, text)
        if text != filtered_text:
            print "Dropping disallowed characters; filtered to:"
            print filtered_text
            text = filtered_text

        # Numerals. Braille "[0-9]" translates up in ASCII space to "#[a-j]".
        text = re.sub('([0-9]+)',
            # The lambda translates capture group \1.
            lambda match: "#" + ''.join(numeral_to_character(c) for c in match.group(1)),
            text,
        )

        return text

    @returns([np.ndarray])
    @params(self=object, text=str)
    def text_to_braille(self, text):
        '''Translates text into braille chars represented as 2x3 numpy arrays'''
        text = self.normalize(text)
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

    @returns(np.ndarray)
    @params(self=object, text=str, char_width=int, dot_margin=int, dot_padding=int)
    def text_line_to_pixels(self, text, char_width, dot_margin, dot_padding):
        '''
        Convert a single line of text to a braille representation on a wrapped
        spaced grid.
        '''
        pixels = dotgrid_to_pixels(
            self.braille_to_dotgrid(
                self.text_to_braille(text), width=char_width),
            padding=dot_padding)
        pixels = add_margin(pixels, dot_margin)
        return pixels

    @returns(Image.Image)
    @params(self=object, lines=[str], char_width=int, dot_margin=int, dot_padding=int)
    def convert(self, lines, char_width=10, dot_margin=1, dot_padding=1):
        '''Convert multiline text to a braille dotgrid image representation'''
        pixels = np.vstack(
            self.text_line_to_pixels(
                line, char_width, dot_margin, dot_padding)
            for line in lines)
        return Image.fromarray(pixels.astype('uint8')*255)


def main():
    parser = OptionParser(usage="usage: python %prog [options] text")
    parser.add_option("-f", "--file", dest="input", type=str,
                      help="input file path; takes precedence over `text` arg")
    parser.add_option("-o", "--output", dest="output", type=str,
                      help="output file path")
    parser.add_option("--show", dest="show", action="store_true",
                      help="show image (defaults to true if no output specified)")
    parser.add_option("--width", dest="width", type=int, default=10,
                      help="grid width in braille characters; default=10")
    parser.add_option("--margin", dest="margin", type=int, default=1,
                      help="margin in dots")
    parser.add_option("--padding", dest="padding", type=int, default=1,
                      help="padding in dots")
    parser.add_option("--dotsize", dest="dot_size", type=int, default=10,
                      help="dot size in pixels")
    (options, args) = parser.parse_args()

    # Obtain text input
    text_lines = args
    if options.input:
        if len(args)>0:
            print "Ignoring text input; using file"
        text_lines = [line.strip() for line in open(options.input, 'r').readlines()]
    else:
        assert len(args)==1, "Must provide input"

    # Setup
    setup_typecheck()
    gen = BrailleImageGenerator()

    # Generate image
    im = gen.convert(
        text_lines,
        char_width=options.width,
        dot_margin=options.margin,
        dot_padding=options.padding,
    )
    im = im.resize((im.size[0]*options.dot_size, im.size[1]*options.dot_size))
    if options.output:
        im.save(options.output)
    if options.show or not options.output:
        im.show()


if __name__ == "__main__":
    main()
