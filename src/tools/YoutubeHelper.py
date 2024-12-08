import discord
import requests
import re
import datetime
from bs4 import BeautifulSoup

from src.tools.logging import logger

class YoutubeHelper:

    def __init__(self) -> None: ...

    async def search_youtube(self, query: str, message: discord.Message | None = None) -> str:
        url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        rep = requests.get(url=url)

        if rep.status_code != 200:
            if message:
                await message.edit(embed=discord.Embed(title="An unexpected error occured.", color=discord.Color.red()))
            return

        soup = BeautifulSoup(rep.text, features="html.parser")
        video_id = re.findall(r'"videoId":"(.*?)"', str(soup.find_all("script")))

        return video_id[0]

    async def identify_link(self, query: str) -> str:
        logger.debug("start identifying")
        if "https://" in query and "youtube" in query:
            logger.debug("yt link")
            return "yt_link"
        elif "https://" in query:
            logger.debug("unknown link")
            return "unknown_link"
        else:
            logger.debug("no link")
            return "no_link"
        

    async def get_yt_title(self, url: str) -> str:

        logger.debug(f"fetching title using a very bad form of abusing the yt api at {datetime.datetime()}")
        rep = requests.get(url)

        soup = BeautifulSoup(rep.text, features="html.parser")
        title = soup.find_all("title")[0]

        logger.debug(f"finished fetching title using a very bad form of abusing the yt api at {datetime.datetime()}")
        return str(title).replace("<title>", "").replace("</title>", "")



yt_helper = YoutubeHelper()