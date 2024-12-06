import argparse
import src.settings as settings

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--mp3', 
        type=str, 
        help='Specify the path to the MP3 directory.',
        default=None
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug mode.")
    parser.add_argument("--test", action="store_true", help="Enable testing mode.")

    args = parser.parse_args()

    settings.mp3_path = args.mp3
    settings.debug_mode = args.debug
    settings.testing_mode = args.test

    from src.tools.logging import logger
    from src.tools.MP3Helper import mp3loader
    
    if args.mp3:
        logger.info(f"Adding MP3 files in {settings.mp3_path} to the queue!")
        mp3loader.add_to_queue()

    if args.debug:
        logger.info(f"Launching in debug mode.", True)

    if args.test:
        logger.info(f"Launching in test mode.", True)

    if not settings.testing_mode:
        from main import harmony
        harmony.run()
    else:
        logger.info("Running tests", True)
        import src.testing.filepathing as file_test
        file_test.main()

if __name__ == "__main__":
    main()

