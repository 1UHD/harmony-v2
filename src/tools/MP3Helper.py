import discord
from mutagen.mp3 import MP3
from src.tools.Queue import queue
from src.tools.Song import Song
from src.tools.logging import logger
import src.settings as settings
import os

class MP3Song(Song):

    def __init__(self, name: str, path: str):
        super().__init__(url=f"{path}{'/' if not path.endswith('/') else ''}{name}")
        self.title = name

    def _get_audio(self) -> discord.FFmpegPCMAudio:
        audio = MP3(self.url)
        
        self.length = round(audio.info.length)
        self.thumbnail = None

        return discord.FFmpegPCMAudio(self.url)

class MP3Loader:
    
    def __init__(self) -> None:
        self.path = settings.mp3_path

    def _update_path(self) -> None:
        self.path = settings.mp3_path

    def _find_files_in_directory(self) -> list[str]:
        self._update_path()

        if not self.path:
            return
        
        mp3_files = []
        
        try:
            for file in os.listdir(self.path):
                if file.endswith(".mp3"):
                    mp3_files.append(file)

        except Exception as e:
            logger.error(f"Couldn't load MP3 files in: {self.path}", True)
            logger.error(e)
            return
        
        return mp3_files
    
    def add_to_queue(self) -> None:
        paths = self._find_files_in_directory()

        if not paths or len(paths) < 1:
            logger.error("No MP3 files were found in that directory!", True)
            return

        for s in paths:
            try:
                song = MP3Song(name=s, path=self.path)

                queue.add(song=song)
            except Exception:
                logger.error(f"'{s}' couldn't be added.", True)


mp3loader = MP3Loader()