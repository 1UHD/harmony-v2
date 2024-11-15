from src.tools.logging import logger
from src.tools.MP3Helper import mp3loader
from src.tools.Queue import queue
from mutagen.mp3 import MP3

class lol1:
    def __init__(self) -> None:
        self.str = "one"
        self.num = 1

    def do_shit(self) -> None:
        logger.debug(f"{self.str}, {self.num}")

class lol2(lol1):
    def do_more_shit(self) -> None:
        self.do_shit()

lel2 = lol2()

def main() -> None:
    logger.debug(queue.get_formatted())