import discord
from discord.ext import commands
import platform
import requests
from bs4 import BeautifulSoup
import re

import src.tools.embeds as embed
from src.tools.logging import logger
from src.tools.Song import Song
from src.tools.Queue import queue
from src.tools.Timer import timer

class QueueCog(commands.Cog):
    
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.opus_loaded = self._load_opus()

    def _load_opus(self) -> bool:
        os = platform.system().lower()

        #TODO: make this awful libopus finder better

        try:
            if os == "darwin":
                discord.opus.load_opus("/opt/homebrew/Cellar/opus/1.5.2/lib/libopus.dylib")
                logger.info("OPUS loaded. (v1.5.2 MacOS, homebrew)", True)
                return True
            
            elif os == "windows":
                discord.opus.load_opus("C:/Windows/System32/opus.dll")
                logger.info("OPUS loaded. (v1.5.2 Windows)")
                return True
            
            else:
                logger.error("You're OS doesn't have a supported OPUS path. Please relaunch the bot using the --custom-opus launch arg and add file called opuspath.txt containing nothing but the path to libopus.", True)
                self.bot.close()
                return False

        except:
            logger.error("OPUS is not installed!", True)
            self.bot.close()
            return False
        

    async def _handle_vc(self, ctx: commands.Context) -> None:
        if not ctx.author.voice:
            await embed.send_error("You're not in a voice channel.", context=ctx)
            return

        if not ctx.voice_client:
            await ctx.author.voice.channel.connect()

        if ctx.voice_client.channel is not ctx.author.voice.channel:
            await ctx.voice_client.disconnect()
            await ctx.author.voice.channel.connect()

    async def _play_next_song(self, ctx: commands.Context) -> None:
        if not ctx.voice_client:
            await embed.send_error("the fucking voice client doesnt fucking exist and i dont fucking know why ", context=ctx)
            return

        if queue.get_length() < 1:
            await embed.send_error("Queue is empty.", context=ctx)
            return
        
        if not ctx.voice_client.is_playing():
            song = queue.get_first_song()
            queue.remove(0)

            timer.start()
            ctx.voice_client.play(song.audio, after=lambda e: ctx.bot.loop.create_task(self._play_next_song(ctx=ctx)))
            await embed.send_embed(title="Song playing", description=song.title, context=ctx)

    def _search_youtube(self, query: str, message: discord.Message | None = None) -> str:
        url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        rep = requests.get(url=url)

        if rep.status_code != 200:
            if message:
                message.edit(embed=discord.Embed(title="An unexpected error occured.", color=discord.Color.red()))
            return

        soup = BeautifulSoup(rep.text, features="html.parser")
        video_id = re.findall(r'"videoId":"(.*?)"', str(soup.find_all("script")))

        return video_id[0]

    @commands.hybrid_group(name="queue", description="Provides information about the queue.")
    async def queue(self, ctx: commands.Context) -> None:
        if not ctx.invoked_subcommand:
            await embed.send_error(title="Wrong usage, see `/help queue` for more info.", context=ctx)

    @queue.command(name="play", description="Plays the queue.")
    async def queue_play(self, ctx: commands.Context) -> None:
        if not self.opus_loaded:
            await self.bot.close()

        await self._handle_vc(ctx=ctx)
        await self._play_next_song(ctx=ctx)

    @commands.hybrid_group(name="add", description="Adds a song to the queue.")
    async def add(self, ctx: commands.Context) -> None:
        if not ctx.invoked_subcommand:
            await embed.send_error(title="Wrong usage, see `/help add` for more info.")

    @add.command(name="url", description="Adds a song to the queue via a YouTube link.")
    async def add_url(self, ctx: commands.Context, url: str) -> None:
        message = await embed.send_embed("Adding song to queue.", context=ctx, color=discord.Color.yellow())

        song = Song(url=url)
        queue.add(song=song)

        await message.edit(embed=discord.Embed(
            title=f"{song.title} has been added to the queue.",
            color=discord.Color.blurple()
        ))

    @add.command(name="search", description="Adds a song to the queue via a prompt.")
    async def add_search(self, ctx: commands.Context, prompt: str) -> None:
        message = await embed.send_embed(title=f"Searching for {prompt}...", color=discord.Color.yellow(), context=ctx)

        video_id = await self._search_youtube(message=message, query=prompt)
        message.edit(embed=discord.Embed(title="Downloading song..."))
        song = Song(url=f"https://www.youtube.com/watch?v={video_id}")
        queue.add(song=song)

        await message.edit(embed=discord.Embed(
            title=f"{song.title} has been added to the queue.",
            color=discord.Color.blurple()
        ))



async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(QueueCog(bot=bot))