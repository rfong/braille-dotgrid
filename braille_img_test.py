# incomplete tests for some finicky bits in braille_img.py

import unittest

from braille_img import *


class TestBrailleImageGenerator(unittest.TestCase):

    def setUpModule(self):
        setup_typecheck()

    gen = None
    def setUp(self):
        self.gen = BrailleImageGenerator()

    def test_text_to_braille(self):
        text = "Hello! hi."  # all chars here correspond to single braille chars
        brs = self.gen.text_to_braille(text)
        self.assertEqual(len(brs), len(text))
        for br in brs:
            self.assertEqual(br.shape, (3,2))

    def test_braille_to_dotgrid(self):
        text = "Hello! hi."
        brs = self.gen.text_to_braille(text)

        # One row
        grid = self.gen.braille_to_dotgrid(brs, width=10)
        self.assertEqual(grid.shape, (3, 2*10))

        # Two rows
        grid = self.gen.braille_to_dotgrid(brs, width=5)
        self.assertEqual(grid.shape, (6, 2*5))

        # Two rows, with some padding
        grid = self.gen.braille_to_dotgrid(brs, width=6)
        self.assertEqual(grid.shape, (6, 2*6))

    def test_normalize(self):
        self.assertEqual(self.gen.normalize("AlpHabEtiCAL"), "alphabetical")
        self.assertEqual(self.gen.normalize("test123!"), "test#bcd!")
        # Should drop non-allowed characters
        self.assertEqual(
            self.gen.normalize("test^* foo123$$bar/"),
            "test foo#bcdbar")

    def test_numeral_to_character(self):
        self.assertEqual(numeral_to_character("0"), "a")
        self.assertEqual(numeral_to_character("1"), "b")
        self.assertEqual(numeral_to_character("2"), "c")
        self.assertEqual(numeral_to_character("3"), "d")
        self.assertEqual(numeral_to_character("4"), "e")
        self.assertEqual(numeral_to_character("5"), "f")
        self.assertEqual(numeral_to_character("6"), "g")
        self.assertEqual(numeral_to_character("7"), "h")
        self.assertEqual(numeral_to_character("8"), "i")
        self.assertEqual(numeral_to_character("9"), "j")

        for i in xrange(10):
            with self.assertRaises(TypeError):
                numeral_to_character(i)


if __name__ == '__main__':
    unittest.main()
