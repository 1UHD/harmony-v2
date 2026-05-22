import discord
from discord.ext import commands
from src.tools.Song import Song
from src.tools.embeds import send_embed
from src.tools.Queue import queue

class SongListPrettifierView(discord.ui.View):
    def __init__(self, title: str, pages: list[str]) -> None:
        super().__init__(timeout=120)
        self.title = title
        self.pages = pages
        self.active_page = 0
        self.update_buttons()

    def update_buttons(self) -> None:
        self.prev_button.disabled = self.active_page == 0
        self.next_button.disabled = self.active_page >= len(self.pages)-1

    @discord.ui.button(label="<", style=discord.ButtonStyle.blurple)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        self.active_page -= 1
        self.update_buttons()

        await interaction.response.edit_message(
            embed=discord.Embed(
                title=f"{self.title} (Page {self.active_page+1}/{len(self.pages)})",
                description=self.pages[self.active_page],
                color=discord.Color.blurple()
            ),
            view=self
        )

    @discord.ui.button(label=">", style=discord.ButtonStyle.blurple)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        self.active_page += 1
        self.update_buttons()

        await interaction.response.edit_message(
            embed=discord.Embed(
                title=f"{self.title} (Page {self.active_page+1}/{len(self.pages)})",
                description=self.pages[self.active_page],
                color=discord.Color.blurple()
            ),
            view=self
        )

    async def on_timeout(self) -> None:
        for item in self.children:
            item.disabled = True

class SongListPrettifier:
    def __init__(self) -> None:
        self.discord_limit = 4096 #max bytes allowed in a discord embed description is 4096

    def prettify(self, songs: list[Song]) -> list[str]:
        title_list = [[]]
        current_bytes = 0
        current_index = 0

        song_index = 1

        for song in songs:
            formatted_title = f"{song_index}. {song.title}\n"
            if current_bytes + len(formatted_title) > self.discord_limit:
                current_bytes = 0
                current_index += 1
                title_list.append([])

            song_index += 1
            current_bytes += len(formatted_title)
            title_list[current_index].append(formatted_title)

        stringified = []
        for l in title_list:
            stringified.append("".join(s for s in l))

        return stringified

    def prettify_duration(self, length: int) -> str:
        if length < 3600:
            return time.strftime("%M:%S", time.gmtime(length))
        else:
            return time.strftime("%H:%M:%S", time.gmtime(length))

    async def send_as_embed(self, title: str, song_list: list[Song], ctx: commands.Context) -> None:
        pages = self.prettify(song_list)
        time_remaining = self.prettify_duration(queue.get_duration())

        if len(pages) == 1:
            await send_embed(
                title=f"{title} (Page 1/1)",
                description=pages[0],
                context=ctx,
                footer=f"Remaining: {time_remaining}"
            )
        else:
            view = SongListPrettifierView(title=title, pages=pages)
            await send_embed(
                title=f"{title} (Page 1/{len(pages)})",
                description=pages[0],
                context=ctx, view=view,
                footer=f"Remaining: {time_remaining}"
            )
        
list_prettifier = SongListPrettifier()