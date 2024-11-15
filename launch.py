import argparse

from main import harmony
from src.tools.logging import logger
from src.tools.MP3Helper import mp3loader
import src.settings as settings
import src.testing.filepathing as file_test

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--mp3', 
        type=str, 
        help='Specify the path to the MP3 directory.',
        default=None
    )
    
    args = parser.parse_args()
    settings.mp3_path = args.mp3
    
    if args.mp3:
        logger.info(f"Adding MP3 files in {settings.mp3_path} to the queue!")
        mp3loader.add_to_queue()

    if not settings.testing_mode:
        harmony.run()
    else:
        logger.info("Running tests")
        file_test.main()

if __name__ == "__main__":
    main()