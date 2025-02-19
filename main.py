import discord
from discord.ext import commands
from src.settings import KEY, LOGO, VERSION, BETA, COGS_DIR, debug_mode, no_update
from src.tools.logging import logger, Colors
from src.tools.PackageManager import packageManager

class Main:

    def __init__(self) -> None:
        self.bot = self._initialize_bot()
        self.bot.event(self.on_ready)

    def _initialize_bot(self) -> commands.Bot:
        intents = discord.Intents.all()
        activity = discord.Streaming(name="random music!", url="https://harmony.dev")
        prefix = "."

        return commands.Bot(command_prefix=prefix, activity=activity, intents=intents, help_command=None, case_insensitive=False)

    def _start_message(self) -> None:
        logger.info(f"{Colors.PURPLE}{LOGO}{Colors.END}Version: {VERSION} {f'({Colors.RED}BETA{Colors.END})' if BETA else None}\n\nBot: {self.bot.user.name} (ID: {self.bot.user.id})\n", True)
        if debug_mode:
            logger.warning("DEBUG MODE is enabled!")

    async def on_ready(self) -> None:
        self._start_message()

        for cog in COGS_DIR.glob("*.py"):
            if cog.name != "__init__.py":
                try:
                    await self.bot.load_extension(f"src.cogs.{cog.name[:-3]}")
                    logger.info(f"Initialized Cog: {cog.name[:-3]}")
                except Exception as e:
                    logger.error(f"Error while loading extension {cog.name}: {e}")

        try:
            await self.bot.tree.sync()
            logger.info("Bot tree synced.")
        except Exception as e:
            logger.error(f"Error while syncing bot tree: {e}")
        

    def run(self) -> None:
        if not no_update:
            packageManager.update_packages()

        logger.info("Launching Harmony", True)
        self.bot.run(token=KEY, log_handler=None)

harmony = Main()