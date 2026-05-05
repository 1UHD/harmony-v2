import time
from typing import override
import discord
from tidalapi.media import Track
import yt_dlp
from src.settings import bitrate
from src.tools.Song import Song
from src.tools.TidalHelper import tidal_helper
from src.tools.logging import logger

class TidalSong(Song):
    track: Track

    def __init__(self, track: Track) -> None:
        self.track = track
        super().__init__()
    
    @override
    def get_metadata(self) -> bool:
        self.title = self.track.title
        self.length = self.track.duration
        artist = self.track.artist
        if artist:
            self.artist = artist.name
        album = self.track.album
        if album:
            self.thumbnail = album.image()
        self.upload_date = str(self.track.tidal_release_date)
        self.likes = self.track.popularity
        self.audio_url = tidal_helper.get_link(self.track)
        logger.debug("Finished gathering song info")
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
