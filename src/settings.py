from src.bot_token import BOT_TOKEN
import pathlib

KEY = BOT_TOKEN

HOME_DIR = pathlib.Path(__file__).parent
COGS_DIR = HOME_DIR / "cogs"

VERSION = "2.0"
BETA = True
LOGO = """
 _   _                                        
| | | | __ _ _ __ _ __ ___   ___  _ __  _   _ 
| |_| |/ _` | '__| '_ ` _ \\ / _ \\| '_ \\| | | |
|  _  | (_| | |  | | | | | | (_) | | | | |_| |
|_| |_|\\__,_|_|  |_| |_| |_|\\___/|_| |_|\\__, |
                                        |___/
"""
debug_mode = True
testing_mode = False

bitrate = 128

mp3_path = None