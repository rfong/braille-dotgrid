braille-dotgrid
-----

Generates a braille dotgrid image from text.
Wrapping is irrespective of word boundaries; this is a stylistic generator for puzzle purposes.

![alphabet](examples/alphabet.bmp)


## Setup

```
pip install -r requirements.txt
```

## Usage examples

- `python braille_img.py --width=6 'Hello world!'`

![](examples/hello6.bmp)

- File I/O: `python braille_img.py --file=hello.txt --output=hello.bmp`

```
Usage: python braille_img.py [options] text

Options:
  -h, --help            show this help message and exit
  -f INPUT, --file=INPUT
                        input file path; takes precedence over `text` arg
  -o OUTPUT, --output=OUTPUT
                        output file path
  --show                show image (defaults to true if no output file
                        specified)
  --width=WIDTH         grid width in braille characters; default=10
  --margin=MARGIN       margin in dots; default=1
  --dotsize=DOT_SIZE    dot size in pixels; default=10
```


## Limitations

Currently supports the following:
```
ABCDEFGHIJKLMNOPQRSTUVWXYZ
abcdefghijklmnopqrstuvwxyz
0123456789
’'! ,.;:?
```

Unsupported characters are dropped.

## References

- https://www.pharmabraille.com/pharmaceutical-braille/the-braille-alphabet/
- https://www.brailletranslator.org/
