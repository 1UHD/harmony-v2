import discord
from discord.ext import commands

import src.tools.embeds as embed
import src.settings as settings
from src.tools.logging import logger
from src.tools.MP3Helper import mp3loader

class MP3Cog(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_group(name="mp3", description="Add mp3 files to the queue!")
    async def mp3(self, ctx: commands.Context) -> None:
        if not ctx.invoked_subcommand:
            await embed.send_error(title="Wrong usage, see `/help mp3` for more info.", context=ctx)

    @mp3.command(name="file", description="Adds a mp3 file to the queue.")
    async def mp3_file(self, ctx: commands.Context, filepath: str) -> None:
        if not settings.mp3_path:
            await embed.send_error(title="Missing path permission!",
                                   description="Launch Harmony using the --mp3 argument to enable MP3 features!",
                                   context=ctx
                                   )
            return
        
        status = mp3loader.add_specific_file(name=filepath)
        if status == "error_not_mp3":
            await embed.send_error(title="Path does not contain an MP3 file", context=ctx)
            return
        
        elif status == "error_not_found":
            await embed.send_error(title="File does not exist", context=ctx)
            return
        
        elif status == "error_adding":
            await embed.send_error(title="File couldn't be added", context=ctx)
            return
        
        else:
            await embed.send_embed(title=f"{status} has been added to the queue", context=ctx)

    @mp3.command(name="directory", description="Adds all mp3 in a directory to the queue.")
    async def mp3_directory(self, ctx: commands.Context, directory: str) -> None:
        if not settings.mp3_path:
            await embed.send_error(title="Missing path permission!",
                                   description="Launch Harmony using the --mp3 argument to enable MP3 features!",
                                   context=ctx
                                   )
            return
        
        if "mp3" in directory:
            await embed.send_error(title="Provided file path, expected directory", context=ctx)
            return
        
        status = mp3loader.add_to_queue(path=directory)
        if status == "error_no_file":
            await embed.send_error(title="Directory does not contain mp3 files")
            return
        
        if status == "error_not_found":
            await embed.send_error(title="Directory does not exist", context=ctx)
            return
        
        else:
            await embed.send_embed(title="Added all available songs", context=ctx)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(MP3Cog(bot=bot))