import time
import discord
import yt_dlp
from src.settings import bitrate
from src.tools.logging import logger

class Song:
    title: str
    thumbnail: str
    artist: str
    artist_subs: int
    views: int
    likes: int
    upload_date: str
    is_restricted: bool
    length: int
    audio_url: str
    audio: None | discord.FFmpegPCMAudio
    
    def __init__(self) -> None:
        self.title = ""
        self.thumbnail = ""
        self.artist = ""
        self.artist_subs = 0
        self.views = 0
        self.likes = 0
        self.upload_date = ""

        self.is_restricted = False
        self.length = 0
        self.audio_url = ""
        self.audio = None
    
    def get_audio(self) -> None:
        self.audio = discord.FFmpegPCMAudio(self.audio_url, before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5")

    def get_metadata(self) -> bool:
        return False

    def prettify_upload_date(self) -> str:
        return f"{self.upload_date[-2:]}.{self.upload_date[-4:-2]}.{self.upload_date[:-4]}"

    def prettify_number(self, value: int) -> str:
        return format(value, ",")

    def prettify_duration(self) -> str:
        if self.length < 3600:
            return time.strftime("%M:%S", time.gmtime(self.length))
        else:
            return time.strftime("%H:%M:%S", time.gmtime(self.length))

    #debug
    def print_self(self) -> None:
        logger.debug(f"Stats for {self}\nTitle: {self.title}\nArtist: {self.artist} [Subs: {self.prettify_number(self.artist_subs)}]\nVideo stats: {self.prettify_number(self.views)} with {self.prettify_number(self.likes)} likes, length: {self.prettify_duration()}\nThumbnail URL: {self.thumbnail}\nUploaded: {self.prettify_upload_date()}")
