import discord
from discord.ext import commands
import platform
import requests
from bs4 import BeautifulSoup
import re
import os

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
        os_name = platform.system().lower()

        try:
            if os_name == "darwin":  # macOS
                opus_path = "/opt/homebrew/lib/libopus.dylib" if os.uname().machine == "arm64" else "/usr/local/lib/libopus.dylib"
                discord.opus.load_opus(opus_path)
                logger.info("OPUS loaded on macOS.")
                return True

            elif os_name == "windows":  # Windows
                opus_path = "C:/Windows/System32/opus.dll"
                discord.opus.load_opus(opus_path)
                logger.info("OPUS loaded on Windows.")
                return True

            elif os_name == "linux":  # Linux
                opus_path = "/usr/lib/x86_64-linux-gnu/libopus.so.0" if os.path.isfile("/usr/lib/x86_64-linux-gnu/libopus.so.0") else "/usr/lib/libopus.so.0"
                discord.opus.load_opus(opus_path)
                logger.info("OPUS loaded on Linux.")
                return True

            else:
                logger.error("Unknown operating system. Rerun Harmony v2 using the flag --custom-opus <path>.", True)
                self.bot.close()
                return False

        except:
            logger.error("OPUS not found. Please install libopus or provide a custom path using the flag --custom-opus <path>.", True)
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
        logger.debug(queue.get_length())
        if not ctx.voice_client:
            return
        
        if ctx.voice_client.is_playing() or queue.is_paused():
            await embed.send_error(title="The bot is already playing.", context=ctx)
            return

        if queue.get_length() < 1 and not queue.is_looped():
            queue.set_current(None)
            await embed.send_error("Queue is empty.", context=ctx)
            return
        
        if not ctx.voice_client.is_playing():
            song = queue.get_song(queue.get_current_index())

            queue.set_current(song=song)
            queue.set_current_index(queue.get_current_index() + 1)

            queue.unpause()

            timer.start()
            ctx.voice_client.play(song.audio, after=lambda e: ctx.bot.loop.create_task(self._play_next_song(ctx=ctx)))
            await embed.send_embed(title="Song playing", description=song.title, context=ctx)

    async def _search_youtube(self, query: str, message: discord.Message | None = None) -> str:
        url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        rep = requests.get(url=url)

        if rep.status_code != 200:
            if message:
                await message.edit(embed=discord.Embed(title="An unexpected error occured.", color=discord.Color.red()))
            return

        soup = BeautifulSoup(rep.text, features="html.parser")
        video_id = re.findall(r'"videoId":"(.*?)"', str(soup.find_all("script")))

        return video_id[0]

    async def _identify_link(self, query: str) -> str:
        if "https://" in query and "youtube" in query:
            return "yt_link"
        elif "https://" in query:
            return "unknown_link"
        else:
            return "no_link"
        
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

    @commands.hybrid_group(name="queue", description="Provides information about the queue.")
    async def queue(self, ctx: commands.Context) -> None:
        if not ctx.invoked_subcommand:
            await embed.send_error(title="Wrong usage, see `/help queue` for more info.", context=ctx)

    @queue.command(name="play", description="Plays the queue.")
    async def queue_play(self, ctx: commands.Context) -> None:
        if not self.opus_loaded:
            await self.bot.close()

        if ctx.voice_client.is_playing():
            await embed.send_error("The bot is already playing.")
            return

        await self._handle_vc(ctx=ctx)
        await self._play_next_song(ctx=ctx)

    @queue.command(name="list", description="Displays the queue.")
    async def queue_list(self, ctx: commands.Context) -> None:
        if queue.get_length() < 1 and not queue.get_current():
            await embed.send_embed(title="The queue is empty.", context=ctx)
            return
        
        remaining_time = queue.get_duration() 

        if queue.get_current():
            remaining_time += queue.get_current().length - round(timer.get_time_elapsed())
        remaining_songs = queue.get_length()

        await embed.send_embed(
            title=f"Currently: {queue.get_current().title if queue.get_current() else 'None'}",
            description=f"{queue.get_formatted()}",
            footer=f"{remaining_songs} song{'s' if queue.get_length() > 1 else ''}; {self._seconds_to_time(remaining_time)} remaining",
            context=ctx
        )

    @queue.command(name="remove", description="Removes a song from the queue.")
    async def queue_remove(self, ctx: commands.Context, index: int) -> None:
        if queue.get_length() < 1:
            await embed.send_error(title="Queue is empty.", context=ctx)
            return
        
        if index == queue.get_current_index():
            await embed.send_error(title="The currently playing song cannot be removed.", context=ctx)
            return
        
        queue.remove(index - 1)

        if index < queue.get_current_index():
            queue.set_current_index(queue.get_current_index() - 1)

        await embed.send_embed(title=f"Removed {index}", context=ctx)

    @queue.command(name="clear", description="Clears the queue.")
    async def queue_clear(self, ctx: commands.Context) -> None:
        if queue.get_length() < 1:
            await embed.send_error(title="Queue is empty.", context=ctx)
            return
        
        if ctx.voice_client.is_playing() or queue.is_paused():
            await embed.send_error(title="The bot is still playing.", context=ctx)
            return
        
        queue.clear()


    @commands.hybrid_command(name="add", description="Adds a song to the queue via a link or YouTube url.")
    async def add(self, ctx: commands.Context, prompt: str) -> None:
        is_link = await self._identify_link(query=prompt)

        message = None
        yt_url = ""

        if is_link == "yt_link":
            message = await embed.send_embed("Adding song to queue.", context=ctx, color=discord.Color.yellow())
            yt_url = prompt
        elif is_link == "unknown_link":
            await embed.send_error(title="Unsupported link.")
            return
        else:
            message = await embed.send_embed(title=f"Searching for {prompt}.", color=discord.Color.yellow(), context=ctx)
            video_id = await self._search_youtube(message=message, query=prompt)
            await message.edit(embed=discord.Embed(title="Adding song to queue.", color=discord.Color.yellow()))
            yt_url = f"https://www.youtube.com/watch?v={video_id}"

        song = Song(url=yt_url)
        queue.add(song=song)

        await message.edit(embed=discord.Embed(
            title=f"{song.title} has been added to the queue.",
            color=discord.Color.blurple()
        ))

    @commands.hybrid_command(name="play", description="Plays the queue.")
    async def play(self, ctx: commands.Context) -> None:
        if not self.opus_loaded:
            await self.bot.close()

        await self._handle_vc(ctx=ctx)
        await self._play_next_song(ctx=ctx)

    @commands.hybrid_command(name="stop", aliases=["stfu"], description="Stops the music.")
    async def stop(self, ctx: commands.Context) -> None:
        if not ctx.voice_client:
            embed.send_error(title="The bot is not playing.", context=ctx)
            return
        
        queue.unpause()
        queue.unloop()
        queue.set_current(None)
        queue.set_current_index(0)
        ctx.voice_client.stop()
        await ctx.voice_client.disconnect()
        await embed.send_embed(title="Stopped music.", context=ctx)

    @commands.hybrid_command(name="pause", description="Pauses the music.")
    async def pause(self, ctx: commands.Context) -> None:
        if not ctx.voice_client or (not ctx.voice_client.is_playing() and not queue.is_paused()):
            await embed.send_embed(title="The bot is not playing.", context=ctx)
            return

        if not queue.is_paused():
            ctx.voice_client.pause()
            timer.pause()
            queue.pause()
            await embed.send_embed(title="The music has been paused.", context=ctx)

        else:
            ctx.voice_client.resume()
            timer.unpause()
            queue.unpause()
            await embed.send_embed(title="The music has been unpaused.", context=ctx)

    @commands.hybrid_command(name="loop", description="Loops the music.")
    async def loop(self, ctx: commands.Context) -> None:
        await embed.send_error(title="Looping is currently unsupported.", context=ctx)

        #TODO: create a working loop command.
        #this commands logic needs to be rewritten, streamed music is only available once
        #so in order to replay a song, the audio must be redownloaded.
        #this creates a lot of issues with the self._play_next_song function as of right now
        """
        if not ctx.voice_client or (not ctx.voice_client.is_playing() and not queue.is_paused()):
            await embed.send_embed(title="The bot is not playing.", context=ctx)
            return

        if not queue.is_looped():
            queue.loop()
            await embed.send_embed(title="The music has been looped.", context=ctx)

        else:
            queue.unloop()
            await embed.send_embed(title="The music has been unlooped.", context=ctx)
        """

    @commands.hybrid_command(name="skip", description="Skips the current song.")
    async def skip(self, ctx: commands.Context) -> None:
        if not ctx.voice_client or (not ctx.voice_client.is_playing() and not queue.is_paused()):
            await embed.send_embed(title="The bot is not playing.", context=ctx)
            return

        ctx.voice_client.stop()
        await embed.send_embed(title="Skipped song.", context=ctx)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(QueueCog(bot=bot))
