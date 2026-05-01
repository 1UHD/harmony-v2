import discord
from discord.ext import commands
import math

import src.tools.embeds as embed
from src.tools.Queue import queue
from src.tools.Timer import timer
from src.tools.logging import logger
from src.tools.Prettifier import list_prettifier
from src.tools.Playlist import playlist_manager, Playlist

class Misc(commands.Cog):
    
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    def _seconds_to_time(self, seconds: int) -> str:
        days, seconds = divmod(seconds, 86400)  # 86400 seconds in a day
        hours, seconds = divmod(seconds, 3600)  # 3600 seconds in an hour
        minutes, seconds = divmod(seconds, 60)  # 60 seconds in a minute

        if days > 0:
            return f"{days:02}:{hours:02}:{minutes:02}:{seconds:02}"
        elif hours > 0:
            return f"{hours:02}:{minutes:02}:{seconds:02}"
        else:
            return f"{minutes:02}:{seconds:02}"

    @commands.hybrid_command(name="playing", description="Provides info on the currently playing song.")
    async def playing(self, ctx: commands.Context) -> None:
        if not ctx.voice_client or (not ctx.voice_client.is_playing() and not queue.is_paused()):
            await embed.send_embed(title="The bot is not playing.", context=ctx)
            return

        time_elapsed = round(timer.get_time_elapsed())
        song_length = queue.get_current().length

        logger.debug(f"{time_elapsed}/{song_length}")

        progress = ["-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-"]
        progress_index = math.ceil(time_elapsed / (song_length / 15)) - 1
        progress[progress_index] = "o"

        current = queue.get_current()

        desc = f"""
            by **{current.artist}**

            {self._seconds_to_time(time_elapsed)} {''.join(i for i in progress)} {self._seconds_to_time(song_length)}

            Views: {current.prettify_number(current.views)}
            Likes: {current.prettify_number(current.likes)}
            Uploaded on {current.prettify_upload_date()}
        """

        await embed.send_embed(
            title=current.title,
            description=desc,
            thumbnail=queue.get_current().thumbnail,
            context=ctx
        )
    
    async def playlist_autocomplete(self, interaction: discord.Interaction, current: str) -> list[discord.app_commands.Choice]:
        filtered = [p for p in playlist_manager.playlists if current.lower() in p.name.lower()]

        return [discord.app_commands.Choice(name=p.name, value=p.name) for p in filtered[:25]]

    @commands.hybrid_command(name="experimental", description="experimental command, might nuke your pc.")
    @discord.app_commands.autocomplete(playlist = playlist_autocomplete)
    async def experimental_command(self, ctx: commands.Context, playlist: str) -> None:
        await embed.send_embed(title=f"You picked: {playlist}", context=ctx)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Misc(bot=bot))