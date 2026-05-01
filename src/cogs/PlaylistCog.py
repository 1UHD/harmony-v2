import discord
from discord.ext import commands
import requests

from src.tools.logging import logger
from src.tools.Playlist import playlist_manager
from src.tools.Queue import queue
from src.tools.Song import Song
from src.tools.MP3Helper import MP3Song
from src.tools.YoutubeHelper import yt_helper
from src.tools.Prettifier import list_prettifier
import src.tools.embeds as embed

class PlaylistCog(commands.Cog):
    
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def playlist_autocomplete(self, interaction: discord.Interaction, current: str) -> list[discord.app_commands.Choice]:
        filtered = [p for p in playlist_manager.playlists if current.lower() in p.name.lower()]

        return [discord.app_commands.Choice(name=p.name, value=p.name) for p in filtered[:25]]

    @commands.hybrid_group(name="playlist", description="Playlist Utility.")
    async def playlist(self, ctx: commands.Context) -> None:
        if not ctx.invoked_subcommand:
            await embed.send_error(title="Wrong usage, see `/help queue` for more info.", context=ctx)

    @playlist.command(name="create", description="Creates a playlist.")
    async def playlist_create(self, ctx: commands.Context, name: str) -> None:
        if not playlist_manager.is_available(name=name):
            await embed.send_embed(title="This playlist name is already in use.", context=ctx)
            return

        playlist_manager.create_playlist(name=name)

        await embed.send_embed(title=f"Playlist {name} has been created.", context=ctx)
    
    @playlist.command(name="addcurrent", description="Adds the current song to a playlist.")
    @discord.app_commands.autocomplete(playlist=playlist_autocomplete)
    async def playlist_addcurrent(self, ctx: commands.Context, playlist: str) -> None:
        if not ctx.voice_client or (not ctx.voice_client.is_playing() and not queue.is_paused()):
            await embed.send_error(title="The bot is not playing.", context=ctx)
            return
        
        if playlist_manager.is_available(playlist):
            await embed.send_error(title=f"Playlist {playlist} doesn't exist.", context=ctx)
            return
        
        current = queue.get_current()

        if isinstance(current, MP3Song):
            await embed.send_error(title=f"MP3 songs cannot be stored in Playlists as of right now.", context=ctx)
            return
        
        playlist_object = playlist_manager.get_playlist_object_by_name(name=playlist)
        playlist_manager.add_song(song=current, pl=playlist_object)
        await embed.send_embed(title=f"{current.title} has been added to {playlist_object.name}.", context=ctx)

    @playlist.command(name="add", description="Adds a song to a playlist via a link or YouTube url.")
    @discord.app_commands.autocomplete(playlist = playlist_autocomplete)
    async def playlist_add(self, ctx: commands.Context, playlist: str, prompt: str) -> None:
        if playlist_manager.is_available(name=playlist):
            await embed.send_error(title=f"Playlist {playlist} doesn't exist.", context=ctx)
            return
        
        playlist_object = playlist_manager.get_playlist_object_by_name(name=playlist)
        is_link = await yt_helper.identify_link(query=prompt)

        message = None
        await ctx.interaction.response.defer()
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

        song = Song(url=yt_url)
        song_success = song.get_audio()

        if not song_success:
            await message.edit(embed=discord.Embed(title="There was an error while fetching the audio.", color=discord.Color.red()))
            return

        playlist_manager.add_song(song=song, pl=playlist_object)

        await message.edit(embed=discord.Embed(title=f"{song.title} has been added to the playlist.", color=discord.Color.blurple()))
        

    @playlist.command(name="queue", description="Adds a playlist to the queue.")
    @discord.app_commands.autocomplete(playlist = playlist_autocomplete)
    async def playlist_queue(self, ctx: commands.Context, playlist: str) -> None:
        if playlist_manager.is_available(name=playlist):
            await embed.send_error(title=f"Playlist {playlist} doesn't exist.", context=ctx)
            return
        
        playlist_object = playlist_manager.get_playlist_object_by_name(name=playlist)
        if playlist_object.get_song_amount() < 1:
            await embed.send_error(title=f"{playlist_object.name} is empty.", context=ctx)
            return
        
        await ctx.interaction.response.defer()
        logger.debug("interaction was saved")
        
        message = await embed.send_embed(title=f"Adding {playlist_object.get_song_amount()} song{'s' if playlist_object.get_song_amount() != 1 else ''}", context=ctx, color=discord.Color.yellow())
        logger.debug("trying to queue songs in playlist")
        playlist_manager.queue(pl=playlist_object)
        logger.debug("queued playlist")
        await message.edit(embed=discord.Embed(title=f"{playlist} has been added to the queue.", color=discord.Color.blurple()))

    @playlist.command(name="remove", description="Removes a song from the playlist.")
    @discord.app_commands.autocomplete(playlist = playlist_autocomplete)
    async def playlist_remove(self, ctx: commands.Context, playlist: str, index: int) -> None:
        if playlist_manager.is_available(name=playlist):
            await embed.send_error(title=f"Playlist {playlist} doesn't exist.", context=ctx)
            return
        
        playlist_object = playlist_manager.get_playlist_object_by_name(name=playlist)
        if playlist_object.get_song_amount() < 1:
            await embed.send_error(title=f"{playlist} is empty. You can't remove a song from an empty playlist.", context=ctx)
            return
        
        if playlist_object.get_song_amount() < index:
            await embed.send_error(title=f"Song {index} does not exist.", context=ctx)
            return

        song_title = playlist_object.songs[index-1].title
        playlist_manager.remove_song(pl=playlist_object, index=index)

        await embed.send_embed(title=f"{song_title} has been removed.", context=ctx)

    @playlist.command(name="delete", description="Deletes a playlist.")
    @discord.app_commands.autocomplete(playlist = playlist_autocomplete)
    async def playlist_delete(self, ctx: commands.Context, playlist: str) -> None:
        if playlist_manager.is_available(name=playlist):
            await embed.send_error(title=f"Playlist {playlist} doesn't exist.", context=ctx)
            return
        
        playlist_object = playlist_manager.get_playlist_object_by_name(name=playlist)
        playlist_manager.remove_playlist(playlist_object)
        await embed.send_embed(title=f"Playlist {playlist} has been deleted.", context=ctx)

    @playlist.command(name="info", description="Provides info about a playlist.")
    @discord.app_commands.autocomplete(playlist = playlist_autocomplete)
    async def playlist_info(self, ctx: commands.Context, playlist: str) -> None:
        if playlist_manager.is_available(name=playlist):
            await embed.send_error(title=f"Playlist {playlist} doesn't exist.", context=ctx)
            return
        
        playlist_object = playlist_manager.get_playlist_object_by_name(name=playlist)

        if playlist_object.get_song_amount() < 1:
            await embed.send_error(title="Playlist is empty.", context=ctx)
            return

        await list_prettifier.send_as_embed(title=playlist, song_list=playlist_object.songs, ctx=ctx)
        

    @playlist.command(name="list", description="Lists all playlists.")
    async def playlist_list(self, ctx: commands.Context) -> None:
        playlists = playlist_manager.playlists

        if len(playlists) == 0:
            await embed.send_error(title="No playlists available.", context=ctx)
            return

        await embed.send_embed(title="Available playlists:", description="".join(f"{p.name} - {len(p.songs)} songs\n" for p in playlists), context=ctx)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(PlaylistCog(bot=bot))