from src.tools.logging import logger
from src.tools.MP3Helper import mp3loader
from src.tools.Queue import queue
from src.tools.Playlist import PlaylistManager
from src.tools.YoutubeHelper import yt_helper
from src.tools.setup import setup
from src.tools.PackageManager import packageManager, projectUpdater

def main() -> None:
    logger.debug("Running test filepathing")
    logger.debug(projectUpdater._get_latest_version())
    logger.debug(projectUpdater._get_current_version())
    logger.debug(projectUpdater._get_latest_version() > projectUpdater._get_current_version())