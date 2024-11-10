import discord
from discord.ext import commands

from src.tools.logging import logger

async def send_embed(title: str,
                    description: str = None,
                    footer: str = None,
                    thumbnail: str = None,
                    image: str = None,
                    interaction: discord.Interaction = None,
                    context: commands.Context = None,
                    color: discord.Color = discord.Color.blurple(),
                    view: discord.ui.View = None,
                    delete_after: float | None = None,
                    ephemeral: bool = False,
                    silent: bool = False
                    ) -> discord.Message | None:
    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )
    
    if footer:
        embed.set_footer(text=footer)

    if thumbnail:
        logger.debug(thumbnail)
        embed.set_thumbnail(url=thumbnail)

    if image:
        embed.set_image(url=image)

    if interaction:
        message = await interaction.response.send_message(embed=embed, view=view, delete_after=delete_after, ephemeral=ephemeral, silent=silent)
        return message
    
    elif context:
        message = await context.send(embed=embed, view=view, delete_after=delete_after, ephemeral=ephemeral, silent=silent)
        return message
    
    else:
        return


async def send_error(title: str,
                    description: str = None,
                    interaction: discord.Interaction = None,
                    context: commands.Context = None,
                    view: discord.ui.View = None,
                    delete_after: float | None = None,
                    ephemeral: bool = False,
                    silent: bool = False
                    ) -> discord.Message | None:
    embed = discord.Embed(
        title=title,
        description=description,
        color=discord.Color.red()
    )
    if interaction:
        message = await interaction.response.send_message(embed=embed, view=view, delete_after=delete_after, ephemeral=ephemeral, silent=silent)
        return message
    
    elif context:
        message = await context.send(embed=embed, view=view, delete_after=delete_after, ephemeral=ephemeral, silent=silent)
        return message 
    
    else:
        return

    
async def send_dm(member: discord.Member,
                title: str,
                description: str = None,
                view: discord.ui.View = None,
                delete_after: float | None = None,
                ephemeral: bool = False,
                silent: bool = False
                ) -> discord.Message | None:
    embed = discord.Embed(
        title=title,
        description=description,
        color=discord.Color.blurple()
    )

    message = await member.send(embed=embed, view=view, delete_after=delete_after, ephemeral=ephemeral, silent=silent)
    return message