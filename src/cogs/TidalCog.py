import discord
from discord.ext import commands
import tidalapi
from tidalapi.album import Album
from tidalapi.media import Track
from tidalapi.playlist import Playlist

from src.settings import tidal as tidal_enabled
from src.tools import embeds
from src.tools.Queue import queue
from src.tools.Selections import Collection, CollectionSelectView, SongSelectView
from src.tools.TidalHelper import tidal_helper
from src.tools.TidalSong import TidalSong
from src.tools.logging import logger

class TidalCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if not tidal_enabled:
            await embeds.send_error(title="Tidal support is not enabled.", interaction=interaction)
            return False
        
        return True

    @commands.hybrid_group(name="tidal", description="Provides access to the tidal api")
    async def tidal(self, ctx: commands.Context) -> None:
        if not ctx.invoked_subcommand:
            await embeds.send_error(title="Wrong usage, see `/help tidal` for more info.", context=ctx)

    @tidal.command(name="help", description="Provides help info for tidal")
    async def help(self, ctx: commands.Context) -> None:
        await embeds.send_embed(title="""
           The tidal module gives access to the streaming service tidal through the following subcommands.
           add: Adds a track to the queue
                optional parameter max_results can be increased for a selection menu
           album: Adds the tracks of an album to the queue
                optional parameter max_results can be increased for a selection menu
        """, context=ctx)

    @tidal.command(name="add", description="Add a tidal track to the queue")
    async def add(self, ctx: commands.Context, prompt: str, max_results: int = 1) -> None:
        message = await embeds.send_embed(title=f"Searching for {prompt}.", color=discord.Color.yellow(), context=ctx)
        results = tidal_helper.query(prompt, limit=max_results)
        if max_results == 1:
            track = results["top_hit"]
            song = TidalSong(track)
            if not song.get_metadata():
                logger.error("Failed to get metadata for song")
                return
            queue.add(song)
            await message.edit(embed=discord.Embed(title=f"Adding track to queue", color=discord.Color.blurple()))

            await queue.load_songs()
            try:
                await embeds.send_embed(title=f"{song.title} has been added to the queue.",
                    context=ctx)
            except Exception as e:
                logger.error(e)
        else:
            tracks = results["tracks"][:max_results]
            songs = [TidalSong(track) for track in tracks]
            for song in songs:
                if not song.get_metadata():
                    logger.error("Failed to get metadata for song")
                    return
            view = SongSelectView(songs, ctx, message)
            await message.edit(embed=discord.Embed(title=f"Created song selection dialog", color=discord.Color.blurple()))
            await ctx.send("Select a song:", view=view)

    @tidal.command(name="album", description="Add a tidal album to the queue")
    async def album(self, ctx: commands.Context, prompt: str, max_results: int = 1) -> None:
        await self._collection(ctx, prompt, max_results, [Album])

    @tidal.command(name="playlist", description="Add a tidal playlist to the queue")
    async def playlist(self, ctx: commands.Context, prompt: str, max_results: int = 1) -> None:
        await self._collection(ctx, prompt, max_results, [Playlist])

    @tidal.command(name="collection", description="Add a tidal album or playlist to the queue")
    async def collection(self, ctx: commands.Context, prompt: str, max_results: int = 1) -> None:
        await self._collection(ctx, prompt, max_results, [Playlist, Album])

    async def _collection(self, ctx: commands.Context, prompt: str, max_results: int=1, coll_types = [Album]) -> None:
        message = await embeds.send_embed(title=f"Searching for {prompt}.", color=discord.Color.yellow(), context=ctx)
        results = tidal_helper.query(prompt, max_results, coll_types)
        if max_results == 1:
            collection = results["top_hit"]
            if not collection:
                await embeds.send_error(title="Found no results", context=ctx)
                return

            await message.edit(embed=discord.Embed(title=f"Adding tracks to queue",color=discord.Color.yellow()))

            for track in collection.tracks():
                song = TidalSong(track)
                song.get_metadata()
                queue.add(song)

            await queue.load_songs()
            coll_type = ""
            if isinstance(collection, Album):
                coll_type = "album"
            else:
                coll_type = "playlist"

            await message.edit(embed=discord.Embed(title=f"Added {coll_type} {collection.name} with {collection.num_tracks} tracks to the queue", color=discord.Color.blurple()))
        else:
            collections = [Collection(coll) for coll in results["albums"][:max_results]] +\
                    [Collection(coll) for coll in results["playlists"][:max_results]]
            view = CollectionSelectView(collections, ctx, message)
            await message.edit(embed=discord.Embed(title=f"Created collection selection dialog", color=discord.Color.blurple()))
            await ctx.send("Select an album:", view = view)



async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(TidalCog(bot=bot))
