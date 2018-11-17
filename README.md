braille-dotgrid
-----

Generates a braille dotgrid image from text.
Wrapping is irrespective of word boundaries; this is a stylistic generator for puzzle purposes.

![alphabet](examples/alphabet.bmp)


## Usage
`pip install -r requirements.txt`

```
Usage: braille_img.py [options] inputtext

Options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output=OUTPUT
                        output file path
  --show                show image (defaults to true if no output file
                        specified)
  --width=WIDTH         grid width in braille characters
  --margin=MARGIN       margin in dots
  --dotsize=DOT_SIZE    dot size in pixels
```
