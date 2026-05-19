import discord
from discord.ext import commands
import math

import src.tools.embeds as embeds
import src.tools.Song 
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
            await embeds.send_embed(title="The bot is not playing.", context=ctx)
            return

        current = queue.get_current()

        time_elapsed = round(timer.get_time_elapsed())

        progress = ["-"] * 15
        progress_index = math.ceil(time_elapsed / (current.length / 15)) - 1
        progress[progress_index] = "o"

        desc = f"""
            {f"by **{current.artist}**" if current.artist != "" else ""}

            {f"{self._seconds_to_time(time_elapsed)} {''.join(i for i in progress)} {self._seconds_to_time(current.length)}" if current.length > 0 else ""}

            {f"Views: {current.prettify_number(current.views)}" if current.views > 0 else ""}
            {f"Likes: {current.prettify_number(current.likes)}" if current.likes > 0 else ""}
            {f"Uploaded on {current.prettify_upload_date()}" if current.upload_date != "" else ""}
        """

        await embeds.send_embed(
            title=current.title,
            description=desc,
            thumbnail={current.thumbnail if current.thumbnail != "" else None},
            context=ctx
        )
    
    async def playlist_autocomplete(self, interaction: discord.Interaction, current: str) -> list[discord.app_commands.Choice]:
        filtered = [p for p in playlist_manager.playlists if current.lower() in p.name.lower()]

        return [discord.app_commands.Choice(name=p.name, value=p.name) for p in filtered[:25]]

    @commands.hybrid_command(name="experimental", description="experimental command, might nuke your pc.")
    @discord.app_commands.autocomplete(playlist = playlist_autocomplete)
    async def experimental_command(self, ctx: commands.Context, playlist: str) -> None:
        await embeds.send_embed(title=f"You picked: {playlist}", context=ctx)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Misc(bot=bot))
