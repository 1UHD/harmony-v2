import discord
from discord.ext import commands
import requests

from src.tools.logging import logger
from src.tools.Playlist import PlaylistManager
from src.tools.Queue import queue
from src.tools.Song import Song
from src.tools.MP3Helper import MP3Song
from src.tools.YoutubeHelper import yt_helper
import src.tools.embeds as embed

class PlaylistCog(commands.Cog):
    
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_group(name="playlist", description="Playlist Utility.")
    async def playlist(self, ctx: commands.Context) -> None:
        if not ctx.invoked_subcommand:
            await embed.send_error(title="Wrong usage, see `/help queue` for more info.", context=ctx)

    @playlist.command(name="create", description="Creates a playlist.")
    async def playlist_create(self, ctx: commands.Context, name: str) -> None:
        if not PlaylistManager.check_playlist_name_availability(name=name):
            await embed.send_embed(title="This playlist name is already in use.", context=ctx)
            return

        PlaylistManager.create_playlist(name=name)

        await embed.send_embed(title=f"Playlist {name} has been created.", context=ctx)
    
    @playlist.command(name="addcurrent", description="Adds the current song to a playlist.")
    async def playlist_addcurrent(self, ctx: commands.Context, playlist: str) -> None:
        if not ctx.voice_client or (not ctx.voice_client.is_playing() and not queue.is_paused()):
            await embed.send_error(title="The bot is not playing.", context=ctx)
            return
        
        if not PlaylistManager.check_playlist_existence(name=playlist):
            await embed.send_error(title=f"Playlist {playlist} doesn't exist.", context=ctx)
            return
        
        current = queue.get_current()

        if isinstance(current, MP3Song):
            await embed.send_error(title=f"MP3 songs cannot be stored in Playlists as of right now.", context=ctx)
            return
        
        playlist_object = PlaylistManager.find_playlist_object_by_name(name=playlist)
        playlist_object.add_song(song=current.url)
        await embed.send_embed(title=f"{current.title} has been added to {playlist_object.name}.", context=ctx)

    @playlist.command(name="add", description="Adds a song to a playlist via a link or YouTube url.")
    async def playlist_add(self, ctx: commands.Context, playlist: str, prompt: str) -> None:
        if not PlaylistManager.check_playlist_existence(name=playlist):
            await embed.send_error(title=f"Playlist {playlist} doesn't exist.", context=ctx)
            return
        
        playlist_object = PlaylistManager.find_playlist_object_by_name(name=playlist)
        is_link = await yt_helper.identify_link(query=prompt)

        message = None
        yt_url = ""

        if is_link == "yt_link":
            message = await embed.send_embed("Adding song to playlist.", context=ctx, color=discord.Color.yellow())
            yt_url = prompt
        elif is_link == "unknown_link":
            await embed.send_error(title="Unsupported link.", context=ctx)
            return
        else:
            message = await embed.send_embed(title=f"Searching for {prompt}.", color=discord.Color.yellow(), context=ctx)
            video_id = await yt_helper.search_youtube(message=message, query=prompt)
            await message.edit(embed=discord.Embed(title="Adding song to playlist.", color=discord.Color.yellow()))
            yt_url = f"https://www.youtube.com/watch?v={video_id}"

        playlist_object.add_song(yt_url)
        PlaylistManager.add_song_to_playlist(playlist=playlist, url=yt_url)
        await message.edit(embed=discord.Embed(title=f"Song has been added to the playlist.", color=discord.Color.blurple()))
        

    @playlist.command(name="queue", description="Adds a playlist to the queue.")
    async def playlist_queue(self, ctx: commands.Context, playlist: str) -> None:
        if not PlaylistManager.check_playlist_existence(name=playlist):
            await embed.send_error(title=f"Playlist {playlist} doesn't exist.", context=ctx)
            return
        
        playlist_object = PlaylistManager.find_playlist_object_by_name(name=playlist)
        if playlist_object.get_song_amount() < 1:
            await embed.send_error(title=f"{playlist_object.name} is empty.", context=ctx)
            return
        
        message = await embed.send_embed(title=f"Adding {playlist_object.get_song_amount()} song{'s' if playlist_object.get_song_amount() != 1 else ''}", context=ctx, color=discord.Color.yellow())
        PlaylistManager.queue_playlist(playlist=playlist_object)
        await message.edit(embed=discord.Embed(title=f"{playlist} has been added to the queue.", color=discord.Color.blurple()))

    @playlist.command(name="remove", description="Removes a song from the playlist.")
    async def playlist_remove(self, ctx: commands.Context, playlist: str, index: int) -> None:
        if not PlaylistManager.check_playlist_existence(name=playlist):
            await embed.send_error(title=f"Playlist {playlist} doesn't exist.", context=ctx)
            return
        
        playlist_object = PlaylistManager.find_playlist_object_by_name(name=playlist)
        if playlist_object.song_amount < 1:
            await embed.send_error(title=f"{playlist} is empty. You can't remove a song from an empty playlist.", context=ctx)
            return
        
        playlist_object.remove_song(index)
        PlaylistManager.remove_song_from_playlist(playlist=playlist, index=index)
        await embed.send_embed(title=f"{playlist_object.songs[index]} has been removed.", context=ctx)

    @playlist.command(name="delete", description="Deletes a playlist.")
    async def playlist_delete(self, ctx: commands.Context, playlist: str) -> None:
        if not PlaylistManager.check_playlist_existence(name=playlist):
            await embed.send_error(title=f"Playlist {playlist} doesn't exist.", context=ctx)
            return
        
        playlist_object = PlaylistManager.find_playlist_object_by_name(name=playlist)
        name = playlist_object.name
        del playlist_object
        PlaylistManager.remove_playlist_json(playlist=playlist)
        await embed.send_embed(title=f"Playlist {name} has been deleted.")

    @playlist.command(name="info", description="Provides info about a playlist.")
    async def playlist_info(self, ctx: commands.Context, playlist: str) -> None:
        if not PlaylistManager.check_playlist_existence(name=playlist):
            await embed.send_error(title=f"Playlist {playlist} doesn't exist.", context=ctx)
            return
        
        playlist_object = PlaylistManager.find_playlist_object_by_name(name=playlist)
        #TODO: make this look good.
        await embed.send_embed(title=playlist_object.name, description=await playlist_object.get_formatted(), footer=f"{playlist_object.get_song_amount()} song{'s' if playlist_object.get_song_amount() != 1 else ''}", context=ctx)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(PlaylistCog(bot=bot))