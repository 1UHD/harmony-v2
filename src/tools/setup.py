import os
import sys
import importlib.util

class Colors:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

class Setup:

    def __init__(self) -> None:
        self.path = __file__.replace("/tools/setup.py", "/bot_token.py")

    def _check_if_file_exists(self) -> bool:
        return os.path.exists(self.path)
    
    def _create_token_file(self, token: str) -> None:
        with open(self.path, "w") as f:
            f.write(f"BOT_TOKEN = '{token}'")

    def _delete_token_file(self) -> None:
        os.remove(self.path)

    def _setup(self) -> None:
        welcome_message = f"""
{Colors.PURPLE}{Colors.BOLD}SETUP{Colors.END}
Harmony is a self-hosted Discord music bot designed
to enhance your server’s audio experience.

To get started, you’ll need to create a bot on the
Discord Developer Portal. A step-by-step guide is
available on Harmony’s GitHub page to assist you in
the process.

Once your bot is set up, Harmony requires its token to run.
Please enter your bot token below. Rest assured, your token
is stored locally and will never be shared with third parties.

        """

        print(welcome_message)
        bot_token = input(f"{Colors.CYAN}Enter your bot token:{Colors.END} ")
        self._create_token_file(bot_token)

        packages = [
            "discord", "beautifulsoup4", "certifi", "mutagen", "requests", "yt_dlp"
        ]

        for package in packages:
            if not importlib.util.find_spec(package):
                os.system(f"{sys.executable} -m pip install {package}")

setup = Setup()