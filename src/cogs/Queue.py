import discord
from discord.ext import commands

import src.tools.embeds as embed
import src.tools.Queue as queue

class QueueCommands(commands.Cog):
    
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.HybridGroup(name="queue", description="Provides information about the queue.")
    async def queue(self, ctx: commands.Context) -> None:
        embed.send_error(title="Wrong usage, see `/help queue` for more info.", context=ctx)

    @queue.command(name="play", description="Plays the queue.")
    async def queue_play(self, ctx: commands.Context) -> None:
        ...

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(QueueCommands(bot=bot))