import sys

import denverapi.ctext

es = denverapi.ctext.ColoredText.escape

print = denverapi.ctext.print
input = denverapi.ctext.input

original_stdout = sys.stdout
original_stderr = sys.stderr
original_stdin = sys.stdin

root = ""

__version__ = "0.7.0"
