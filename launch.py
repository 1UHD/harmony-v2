import argparse

def main() -> None:
    from src.tools.setup import setup

    if not setup._check_if_file_exists():
        setup._setup()

    if not setup.check_if_packages_exist():
        from src.tools.logging import logger
        logger.error("Some packages are missing. Are you using the correct python executable?")
        logger.error("In case you haven't set up Harmony, try running python launch.py --setup")
        return
    
    import src.settings as settings

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--mp3', 
        type=str, 
        help='Specify the path to the MP3 directory.',
        default=None
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug mode.")
    parser.add_argument("--test", action="store_true", help="Enable testing mode.")
    parser.add_argument("--no-update", action="store_true", help="Disable the auto updater.")
    parser.add_argument("--update", action="store_true", help="Update the bot.")
    parser.add_argument("--tidal", action="store_true", help="Activate Tidal Support.")
    parser.add_argument("--no-playlist", action="store_true", help="Disable playlist loading on launch.")
    parser.add_argument("--setup", action="store_true", help="Initiate bot setup.")

    args = parser.parse_args()

    settings.mp3_path = args.mp3
    settings.debug_mode = args.debug
    settings.testing_mode = args.test
    settings.no_update = args.no_update
    settings.tidal = args.tidal
    settings.no_playlist = args.no_playlist

    from src.tools.logging import logger
    
    if args.no_playlist:
        logger.warning(f"Launching without playlist preloading.", True)

    if args.tidal:
        logger.info(f"Launching with Tidal support.", True)

    if args.mp3:
        logger.info(f"Launching with file access for {settings.mp3_path}.", True)

    if args.debug:
        logger.info(f"Launching in debug mode.", True)

    if args.test:
        logger.info(f"Launching in test mode.", True)

    if args.update:
        from src.tools.PackageManager import projectUpdater
        projectUpdater.update_project()
        return

    if args.setup:
        logger.warning("You're currently trying to force-setup Harmony. Doing this will overwrite your current bot token!", True)

        action = False
        user_input = input("Proceed? [y/N] ")

        if user_input.lower() == "y":
            setup._setup()

        return

    from src.tools.PackageManager import projectUpdater
    projectUpdater.check_for_update()

    if not settings.testing_mode:
        from main import harmony
        harmony.run()
    else:
        logger.info("Running tests", True)
        import src.testing.filepathing as file_test
        file_test.main()

if __name__ == "__main__":
    main()

