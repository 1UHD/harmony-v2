import discord
from discord.ext import commands

async def send_embed(title: str,
                    description: str = None,
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
    if interaction:
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
        message = await interaction.response.send_message(embed=embed, view=view, delete_after=delete_after, ephemeral=ephemeral, silent=silent)
        return message
    
    elif context:
        embed.set_author(name=context.author.name, icon_url=context.author.avatar)
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
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
        message = await interaction.response.send_message(embed=embed, view=view, delete_after=delete_after, ephemeral=ephemeral, silent=silent)
        return message
    
    elif context:
        embed.set_author(name=context.author.name, icon_url=context.author.avatar)
        message = await context.send(embed=embed, view=view, delete_after=delete_after, ephemeral=ephemeral, silent=silent)
        return message 
    
    else:
        return

    
async def send_dm(member: discord.Member,
                title: str,
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
        color=discord.Color.blurple()
    )
    if interaction:
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
    elif context:
        embed.set_author(name=context.author.name, icon_url=context.author.avatar)
    else:
        return

    message = await member.send(embed=embed, view=view, delete_after=delete_after, ephemeral=ephemeral, silent=silent)
    return message