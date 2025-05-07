from src.tools.logging import logger
import yt_dlp

yt_dlp_config = {
    "format" : "bestaudio/best",
    "postprocessors": [{
        "key": "FFmpegExtractAudio",
        "preferredcodec": "mp3",
        "preferredquality": f"128",
    }],
    "noplaylist": True,
    "quiet": True,
    "no-warnings": True,
}

url = ""

with yt_dlp.YoutubeDL(yt_dlp_config) as ydl:
    logger.debug("extracting")
    info_dict = ydl.extract_info(url, download=False)