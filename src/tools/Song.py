import discord

import yt_dlp
from src.settings import bitrate
from src.tools.logging import logger

class Song:

    def __init__(self, url: str) -> None:
        self.url = url
        self.title = ""
        self.thumbnail = ""
        self.length = ""
        self.audio = self._get_audio()

        self.bitrate = bitrate
        self.yt_dlp_options = {
            "format" : "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": f"{self.bitrate}",
            }],
            "noplaylist": True,
            "quiet": True,
        }

    def _get_audio(self) -> discord.FFmpegPCMAudio:
        link = f"https://www.youtube.com/watch?v={self.vid_id}"

        with yt_dlp.YoutubeDL(self.yt_dlp_options) as ydl:
            info_dict = ydl.extract_info(link, download=False)

            self.thumbnail = self._get_thumbnail()
            self.title = info_dict["title"]
            self.length = info_dict["duration"]

            return discord.FFmpegPCMAudio(info_dict["url"], before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5")

    def _get_thumbnail(self) -> str:
        return f"http://img.youtube.com/vi/{self.vid_id}/hqdefault.jpg"