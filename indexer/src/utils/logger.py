import sys
from multiprocessing import current_process, Queue
from time import localtime, strftime
from typing import Optional

import colorama


class Logger:

    VERBOSITY_ERROR: int = 0
    VERBOSITY_WARNING: int = 1
    VERBOSITY_INFO: int = 2
    VERBOSITY_DECISION: int = 3
    VERBOSITY_DEBUG: int = 4

    def __init__(self, path: str, stream_queue: Optional[Queue]=None, verbosity: int = VERBOSITY_INFO):
        colorama.init(autoreset=True)

        self.path: str = path
        self.stream_queue: Optional[Queue] = stream_queue
        self.verbosity: int = verbosity

    def debug(self, text: str):
        if self.verbosity < Logger.VERBOSITY_DEBUG:
            return

        dt = strftime('%Y-%m-%d %H:%M:%S', localtime())
        sys.stdout.write('{} {:<11} \033[1;36m[debug]    {}\n'.format(dt, current_process().name, text))

    def decision(self, text: str):
        if self.verbosity < Logger.VERBOSITY_DECISION:
            return

        dt = strftime('%Y-%m-%d %H:%M:%S', localtime())
        sys.stdout.write('{} {:<11} \033[1;32m[decision] {}\n'.format(dt, current_process().name, text))

    def error(self, text: str):
        if self.verbosity < Logger.VERBOSITY_ERROR:
            return

        dt = strftime('%Y-%m-%d %H:%M:%S', localtime())
        sys.stderr.write('{} {:<11} \033[1;31m[error]    {}\n'.format(dt, current_process().name, text))

    def info(self, text: str):
        if self.verbosity < Logger.VERBOSITY_INFO:
            return

        dt = strftime('%Y-%m-%d %H:%M:%S', localtime())
        sys.stdout.write('{} {:<11}            {}\n'.format(dt, current_process().name, text))

    def warn(self, text: str):
        if self.verbosity < Logger.VERBOSITY_WARNING:
            return

        dt = strftime('%Y-%m-%d %H:%M:%S', localtime())
        sys.stdout.write('{} {:<11} \033[1;33m[warning]  {}\n'.format(dt, current_process().name, text))

    def stream(self, stream: str, text: str):
        if self.stream_queue is None:
            return
        self.stream_queue.put((stream, text + '\n'))
