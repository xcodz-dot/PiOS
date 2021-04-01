from io import StringIO
from threading import Thread
from typing import Tuple

from pios.core.syscalls import *


def redirect_io(server: Tuple[str, int], authentication: str):
    file = s.makefile("w", buffering=None)
    sys.stdout = file
    sys.stderr = file
    sys.stdin = s.makefile("r", buffering=None)


def redirect_io_to_console():
    sys.stdout = original_stdout
    sys.stderr = original_stderr
    sys.stdin = original_stdin
