import sys

import denverapi.colored_text as ctext

es = ctext.escape

print = ctext.print
input = ctext.input

original_stdout = sys.stdout
original_stderr = sys.stderr
original_stdin = sys.stdin

root = ""

__version__ = "0.7.0"
