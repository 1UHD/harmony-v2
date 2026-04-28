import json
import asyncio
from src.tools.Song import Song
from src.tools.logging import logger
from src.tools.MP3Helper import mp3loader
from src.tools.Queue import queue
from src.tools.Playlist import PlaylistManager
from src.tools.YoutubeHelper import yt_helper
from src.tools.setup import setup
from src.tools.PackageManager import packageManager, projectUpdater

def main() -> None:
    #logger.debug("Running test filepathing")
    #logger.debug(projectUpdater._get_latest_version())
    #logger.debug(projectUpdater._get_current_version())
    #logger.debug(projectUpdater._get_latest_version() > projectUpdater._get_current_version())
    video_id = asyncio.run(yt_helper.search_youtube("never gonna give you up"))
    yt_url = yt_helper.id_to_link(video_id)
    song = Song(yt_url)
    song.get_audio()
    song.print_self()

    #with open("/Users/kurt/Documents/Programming/harmony-v2/src/testing/info_dict.txt", "w") as file:
    #    file.write(json.dumps(info_dict, indent=4))

