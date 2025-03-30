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
        self.title = name.replace(".mp3", "")

    def _get_audio(self) -> discord.FFmpegPCMAudio:
        audio = MP3(self.url)
        
        self.length = round(audio.info.length)
        self.thumbnail = None

        return discord.FFmpegPCMAudio(self.url)

class MP3Loader:
    
    def __init__(self) -> None:
        self.path = settings.mp3_path

    def _correct_path(self, path: str) -> str:
        if path.split("")[-1] is not "/":
            return path + "/"
        else:
            return path
        
    def _correct_file_path(self, path: str) -> str:
        if path.split("")[0] is not "/":
            return "/" + path
        else:
            return path

    def _update_path(self) -> None:
        self.path = self._correct_path(settings.mp3_path)

    def _find_files_in_directory(self, dir_path: str) -> list[str]:
        self._update_path()

        if not self.path:
            return
        
        mp3_files = []
        
        try:
            for file in os.listdir(dir_path):
                if file.endswith(".mp3"):
                    mp3_files.append(file)

        except Exception as e:
            logger.error(f"Couldn't load MP3 files in: {dir_path}", True)
            logger.error(e)
            return
        
        mp3_files = sorted(mp3_files)
        return mp3_files
    
    def add_to_queue(self, path: str) -> str:
        self._update_path()

        dir_path = self.path + self._correct_file_path(path=path)
        if not os.path.exists(path=dir_path):
            return "error_not_found"

        paths = self._find_files_in_directory(dir_path=dir_path)

        if not paths or len(paths) < 1:
            return "error_no_file"

        for s in paths:
            try:
                song = MP3Song(name=s, path=self.path)

                queue.add(song=song)

            except Exception:
                pass

        return "success"

    def add_specific_file(self, name: str) -> str:
        self._update_path()

        name = self._correct_file_path(path=name)

        if "mp3" not in name:
            return "error_not_mp3"

        file_path = self.path + name
        file_name = name.replace("\\", "/").split("/")[-1].split(".")[0]

        if not os.path.exists(path=file_path):
            return "error_not_found"

        try:
            song = MP3Song(name=file_name, path=file_path)
            queue.add(song=song)
            return file_name
        
        except:
            return "error_adding"


mp3loader = MP3Loader()