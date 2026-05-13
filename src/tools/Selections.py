import discord
from collections.abc import Sequence

from discord.ext.commands import Context
from tidalapi.album import Album
from tidalapi.artist import Artist
from tidalapi.media import Track
from tidalapi.playlist import Playlist

from src.tools.TidalSong import TidalSong
from src.tools.embeds import send_embed
from src.tools.Queue import queue
from src.tools.Song import Song
from src.tools.logging import logger

class SongSelect(discord.ui.Select):
    def __init__(self, songs: Sequence[Song], context: Context, status_msg: discord.Message):
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
        self.status_msg = status_msg
        super().__init__(placeholder="Choose a track...", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        logger.debug("Adding song")
        song_id = int(self.values[0])
        song = self.songs[song_id]
        if song.get_metadata():
            queue.add(song)
        await queue.load_songs()
        await self.status_msg.edit(embed=discord.Embed(title=f"Added {song.title} to the queue"))
        self.disabled = True
        self.placeholder = song.title[:100]
        await interaction.edit_original_response(view=self.view)

class SongSelectView(discord.ui.View):
    def __init__(self,songs: Sequence[Song], context: Context, status_msg: discord.Message):
        super().__init__(timeout=30)
        self.add_item(SongSelect(songs, context, status_msg))

class Collection:
    name: None|str
    artist_name: None|str
    tracks: list[Track]
    num_tracks: int
    collection_type: str

    def __init__(self, object: Album|Playlist):
        coll_type = type(object)
        if coll_type != Album and coll_type != Playlist:
            return

        self.name = object.name
        self.tracks = object.tracks()
        self.num_tracks = object.num_tracks
        if isinstance(object,Album):
            self.artist_name = object.artist.name
            self.collection_type = "Album"
        elif isinstance(object, Playlist):
            creator = object.creator
            if isinstance(creator, Artist):
                self.artist_name = creator.name
            else:
                self.artist_name = ""
            self.collection_type = "Playlist"
        

class CollectionSelect(discord.ui.Select):
    def __init__(self,collections:Sequence[Collection], context: Context, status_msg: discord.Message):
        options = [
            discord.SelectOption(
                label=f"{collections[i].name}",
                description=f"{collections[i].artist_name}",
                value=str(i)
            )
            for i in range(min(len(collections), 10))
        ]
        self.collections = collections
        self.context = context
        self.status_msg = status_msg
        super().__init__(placeholder="Choose a collection...", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        logger.debug("Adding collection")
        collection_id = int(self.values[0])
        collection = self.collections[collection_id]
        for track in collection.tracks:
            song = TidalSong(track)
            if song.get_metadata():
                queue.add(song)
        await queue.load_songs()
        coll_type = collection.collection_type
        await self.status_msg.edit(embed=discord.Embed(title=f"Added {coll_type} {collection.name} with {collection.num_tracks} tracks to the queue")
        self.disabled = True
        self.placeholder = collection.name[:100]
        await interaction.edit_original_response(view=self.view)


class CollectionSelectView(discord.ui.View):
    def __init__(self,collections: Sequence[Collection], context: Context):
        super().__init__(timeout=30)
        self.add_item(CollectionSelect(collections, context, status_msg))
