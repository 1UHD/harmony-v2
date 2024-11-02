import discord
from discord.ext import commands
import platform

import src.tools.embeds as embed
from src.tools.logging import logger
from src.tools.Song import Song
from src.tools.Queue import queue
from src.tools.Timer import timer

class QueueCog(commands.Cog):
    
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.opus_loaded = self._load_opus()

    def _load_opus(self) -> bool:
        os = platform.system().lower()

        #TODO: make this awful libopus finder better

        try:
            if os == "darwin":
                discord.opus.load_opus("/opt/homebrew/Cellar/opus/1.5.2/lib/libopus.dylib")
                logger.info("OPUS loaded. (v1.5.2 MacOS, homebrew)", True)
                return True
            
            elif os == "windows":
                discord.opus.load_opus("C:/Windows/System32/opus.dll")
                logger.info("OPUS loaded. (v1.5.2 Windows)")
                return True
            
            else:
                logger.error("You're OS doesn't have a supported OPUS path. Please relaunch the bot using the --custom-opus launch arg and add file called opuspath.txt containing nothing but the path to libopus.", True)
                self.bot.close()
                return False

        except:
            logger.error("OPUS is not installed!", True)
            self.bot.close()
            return False
        

    async def _handle_vc(self, ctx: commands.Context) -> None:
        if not ctx.author.voice:
            await embed.send_error("You're not in a voice channel.", context=ctx)
            return

        if not ctx.voice_client:
            await ctx.author.voice.channel.connect()

        if ctx.voice_client.channel is not ctx.author.voice.channel:
            await ctx.voice_client.disconnect()
            await ctx.author.voice.channel.connect()

    async def _play_next_song(self, ctx: commands.Context) -> None:
        if not ctx.voice_client:
            await embed.send_error("the fucking voice client doesnt fucking exist and i dont fucking kinow why ", context=ctx)
            return

        if queue.get_length() < 1:
            embed.send_error("Queue is empty.", context=ctx)
            return
        
        song = queue.get_first_song()

        timer.start()
        ctx.voice_client.play(song.audio, after=lambda e: self.bot.loop.create_task(self._play_next_song(ctx=ctx)))
        await embed.send_embed(title="Song playing", description=song.title, context=ctx)

    @commands.hybrid_group(name="queue", description="Provides information about the queue.")
    async def queue(self, ctx: commands.Context) -> None:
        if not ctx.invoked_subcommand:
            await embed.send_error(title="Wrong usage, see `/help queue` for more info.", context=ctx)

    @queue.command(name="play", description="Plays the queue.")
    async def queue_play(self, ctx: commands.Context) -> None:
        if not self.opus_loaded:
            await self.bot.close()

        await self._handle_vc(ctx=ctx)
        await self._play_next_song(ctx=ctx)

    @queue.command(name="add", description="adds a song to le playlist")
    async def queue_add(self, ctx: commands.Context, url: str) -> None:
        song = Song(url=url)
        queue.add(song=song)
        await embed.send_embed(f"{song.title} has been added to the queue.", context=ctx)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(QueueCog(bot=bot))