import discord
from discord.ext import commands
import pathlib

import src.tools.embeds as embeds
from src.tools.logging import logger
from src.settings import COGS_DIR

class Admin(commands.Cog):
    
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="shutdown", description="Shuts down the bot.")
    @commands.has_permissions(administrator=True)
    async def shutdown(self, ctx: commands.Context) -> None:
        await embeds.send_embed(
            title="Shutting down...",
            context=ctx
        )
        logger.info("Shutting down.", True)
        await self.bot.close()

    @commands.hybrid_command(name="reload", description="Reloads the bot.")
    @commands.has_permissions(administrator=True)
    async def reload(self, ctx: commands.Context) -> None:

        for cog in COGS_DIR.glob("*.py"):
            if cog.name != "__init__.py":
                try:
                    await self.bot.reload_extension(f"cogs.{cog.name[:-3]}")
                    logger.info(f"Reloaded category: {cog.name[:-3]}")
                except Exception as e:
                    logger.error(f"Couldn't reload category {cog.name[:-3]}: {e}")

        await embeds.send_embed(
            title="Reloaded!",
            context=ctx
        )

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Admin(bot=bot))