

import discord
from discord.ext import commands
import tidalapi
from tidalapi.media import Track

from src.tools import embeds
from src.tools.Queue import queue
from src.tools.Selections import SongSelectView
from src.tools.TidalHelper import tidal_helper
from src.tools.TidalSong import TidalSong
from src.tools.logging import logger

class TidalCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_group(name="tidal", description="Provides access to the tidal api")
    async def tidal(self, ctx: commands.Context) -> None:
        if not ctx.invoked_subcommand:
            await embed.send_error(title="Wrong usage, see `/help tidal` for more info.", context=ctx)

    @tidal.command(name="help", description="Provides help info for tidal")
    async def help(self, ctx: commands.Context) -> None:
        await embeds.send_embed("Future help menu.")

    @tidal.command(name="add", description="Add a tidal track to the queue")
    async def add(self, ctx: commands.Context, prompt: str, max_results: int =1) -> None:
        message = await embeds.send_embed(title=f"Searching for {prompt}.", color=discord.Color.yellow(), context=ctx)
        results = tidal_helper.query(prompt, max_results)
        if max_results == 1:
            track = results["top_hit"]
            song = TidalSong(track)
            if not song.get_audio():
                logger.error("Failed to get audio for song")
            queue.add(song)
        else:
            tracks = results["tracks"][:max_results]
            songs = [TidalSong(track) for track in tracks]
            for song in songs:
                if not song.get_audio():
                    logger.error("Failed to get audio for song")
            view = SongSelectView(songs)
            await ctx.send("Select a song:", view=view)

        await message.edit(embed=discord.Embed(title=f"Adding track to queue",color=discord.Color.yellow()))

        current_index = queue.get_current_index()

        if current_index == 0:
            logger.debug("loading song during add command due to index 0")
            queue.load_current_song()

        elif current_index >= len(queue.queue)-2:
            logger.debug("loading song during add command due to high index")
            queue.load_song(len(queue.queue)-1)

        try:
            await embeds.send_embed(title=f"{song.title} has been added to the queue.",
                context=ctx)
        except Exception as e:
            logger.error(e)

    @tidal.command(name="album", description="Add a tidal album to the queue")
    async def album(self, ctx: commands.Context, prompt: str) -> None:
        message = await embeds.send_embed(title=f"Searching for {prompt}.", color=discord.Color.yellow(), context=ctx)
        results = tidal_helper.query(prompt, 1, tidalapi.Album)
        album = results["top_hit"]
        if not album:
            await embeds.send_error(title="Found no results", context=ctx)
            return

        await message.edit(embed=discord.Embed(title=f"Adding tracks to queue",color=discord.Color.yellow()))

        i = 0
        for track in album.items():
            if type(track) == tidalapi.Track:
                i+=1
                song = TidalSong(track)
                song.get_audio()
                queue.add(song)

        current_index = queue.get_current_index()

        if current_index == 0:
            logger.debug("loading song during add command due to index 0")
            queue.load_current_song()

        elif current_index >= len(queue.queue)-2:
            logger.debug("loading song during add command due to high index")
            queue.load_song(len(queue.queue)-1)

        await message.edit(embed=discord.Embed(title=f"Added album {album.name} with {i} tracks to the queue",color=discord.Color.yellow()))



async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(TidalCog(bot=bot))
