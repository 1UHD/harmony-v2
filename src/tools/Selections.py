import discord
from collections.abc import Sequence

from discord.ext.commands import Context
from tidalapi.album import Album

from src.tools.TidalSong import TidalSong
from src.tools.embeds import send_embed
from src.tools.Queue import queue
from src.tools.Song import Song
from src.tools.logging import logger

class SongSelect(discord.ui.Select):
    def __init__(self, songs: Sequence[Song], context: Context):
        options = [
            discord.SelectOption(
                label=f"{songs[i].title}",
                description=f"{songs[i].artist}",
                value=str(i)
            )
            for i in range(min(len(songs), 10))
        ]
        self.songs = songs
        self.context = context
        super().__init__(placeholder="Choose a track...", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        logger.debug("Adding song")
        song_id = int(self.values[0])
        song = self.songs[song_id]
        if song.get_metadata():
            queue.add(song)
        await queue.load_songs()
        await send_embed(title=f"Added {song.title} to the queue",context=self.context)
        self.disabled = True
        self.placeholder = song.title[:100]
        await interaction.edit_original_response(view=self.view)

class SongSelectView(discord.ui.View):
    def __init__(self,songs: Sequence[Song], context: Context):
        super().__init__(timeout=30)
        self.add_item(SongSelect(songs, context))


class AlbumSelect(discord.ui.Select):
    def __init__(self,albums:Sequence[Album], context: Context):
        options = [
            discord.SelectOption(
                label=f"{albums[i].name}",
                description=f"{albums[i].artist.name}",
                value=str(i)
            )
            for i in range(min(len(albums), 10))
        ]
        self.albums = albums
        self.context = context
        super().__init__(placeholder="Choose an album...", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        logger.debug("Adding album")
        album_id = int(self.values[0])
        album = self.albums[album_id]
        for track in album.tracks():
            song = TidalSong(track)
            if song.get_metadata():
                queue.add(song)
        await queue.load_songs()
        await send_embed(title=f"Added album {album.name} with {album.num_tracks} tracks to the queue",context=self.context)
        self.disabled = True
        self.placeholder = album.name[:100]
        await interaction.edit_original_response(view=self.view)


class AlbumSelectView(discord.ui.View):
    def __init__(self,albums: Sequence[Album], context: Context):
        super().__init__(timeout=30)
        self.add_item(AlbumSelect(albums, context))
