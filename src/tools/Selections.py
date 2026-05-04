import discord
from collections.abc import Sequence

from src.tools import embeds
from src.tools.Queue import queue
from src.tools.Song import Song

class SongSelect(discord.ui.Select):
    def __init__(self, songs: list[Song]):
        options = [
            discord.SelectOption(
                label=f"{songs[i].title}",
                description=f"{songs[i].artist}",
                value=str(i)
            )
            for i in range(min(len(songs), 10))
        ]
        super().__init__(placeholder="Choose a track...", options=options, min_values=1, max_values=1)

class SongSelectView(discord.ui.View):
    def __init__(self,songs: Sequence[Song]):
        super().__init__(timeout=30)
        self.songs = songs
        self.add_item(SongSelect(songs))

    async def select_callback(self, interaction: discord.Interaction):
        song_id = int(interaction.values[0])
        song = self.songs[song_id]
        queue.add(song)
        # TODO add messages
