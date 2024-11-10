import discord

import yt_dlp
from src.settings import bitrate
from src.tools.logging import logger

class Song:

    def __init__(self, url: str) -> None:
        self.url = url
        self.title = ""
        self.thumbnail = ""
        self.length = 0
        self.audio = self._get_audio()

    def _get_audio(self) -> discord.FFmpegPCMAudio:
        ytdlp = {
            "format" : "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": f"{bitrate}",
            }],
            "noplaylist": True,
            "quiet": True,
            "no-warnings": True,
        }

        with yt_dlp.YoutubeDL(ytdlp) as ydl:
            info_dict = ydl.extract_info(self.url, download=False)

            self.thumbnail = self._get_thumbnail()
            self.title = info_dict["title"]
            self.length = info_dict["duration"]

            return discord.FFmpegPCMAudio(info_dict["url"], before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5")

    def _get_thumbnail(self) -> str:
        return f"http://img.youtube.com/vi/{self.url}/hqdefault.jpg"