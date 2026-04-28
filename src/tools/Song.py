import time
import discord
import yt_dlp
from src.settings import bitrate
from src.tools.logging import logger

class Song:

    def __init__(self, url: str) -> None:
        self.url = url

        self.title = ""
        self.thumbnail = ""
        self.artist = ""
        self.artist_subs = 0
        self.views = 0
        self.likes = 0
        self.upload_date = 0

        self.is_restricted = False
        self.length = 0
        self.audio = None

    def get_audio(self) -> bool:
        if self.audio:
            logger.warning("ffmpeg audio already exists, aborting", False)
            return False

        ytdlp = {
            "format" : "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": f"{bitrate}",
            }],
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
        }

        logger.debug("gathering song info")
        with yt_dlp.YoutubeDL(ytdlp) as ydl:
            try:
                info_dict = ydl.extract_info(self.url, download=False)
            except Exception as e:
                self.is_restricted = True
                logger.error(f"couldnt fetch video: {e}")
                return False

            self.title = info_dict["title"]
            self.length = info_dict["duration"]
            self.thumbnail = info_dict["thumbnail"]
            self.views = info_dict["view_count"]
            self.artist = info_dict["channel"]
            self.artist_subs = info_dict["channel_follower_count"]
            self.likes = info_dict["like_count"]
            self.upload_date = info_dict["upload_date"]

            self.audio = discord.FFmpegPCMAudio(info_dict["url"], before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5")
        
        logger.debug("finished gathering song info")

        return True

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

    #legacy
    def _get_thumbnail(self) -> str:
        vid_id = self.url.replace("https://www.youtube.com/watch?v=", "")

        return f"http://img.youtube.com/vi/{vid_id}/hqdefault.jpg"
