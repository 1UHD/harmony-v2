from src.tools.logging import logger
from src.tools.MP3Helper import mp3loader
from src.tools.Queue import queue
from src.tools.Playlist import PlaylistManager
from src.tools.YoutubeHelper import yt_helper

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
lel1 = lol1()

def main() -> None:
    yt_helper.get_yt_nonsense(url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")

    """for i in PlaylistManager.playlists:
        logger.debug(f"NAME: {i.name}, SONGS: {i.songs}")"""

    #PlaylistManager.remove_song_from_playlist("testing", 2)