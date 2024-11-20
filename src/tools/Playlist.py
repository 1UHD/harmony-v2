import os
import json

from src.tools.Song import Song
from src.tools.logging import logger

class Playlist:

    def __init__(self, name: str) -> None:
        self.name = name
        self.songs = []
        self.length = None
        self.song_amount = 0

    def add_song(self, song: str) -> None:
        self.songs.append(song)

class PlaylistUtility:

    def __init__(self) -> None:
        self.path = __file__.replace("/src/tools/Playlist.py", "/playlists/")
        self.playlists = []
        self._initialize_filepath()

    def _initialize_filepath(self) -> None:
        if not os.path.exists(self.path):
            os.mkdir(self.path)

        playlists = self._get_all_playlists()
        
        if playlists:
            for playlist in playlists:
                self.read_playlist(playlist)
        else:
            logger.info("Didn't find any playlists.")

    def _get_all_playlists(self) -> list[str]:
        
        playlist_files = []

        try:
            for file in os.listdir(self.path):
                if file.endswith(".json"):
                    playlist_files.append(file)

        except Exception as e:
            logger.error("Coudln't load playlists.", True)
            logger.error(e)
            return
        
        return playlist_files
        
    def create_playlist_json(self, name: str, urls: list[str]) -> None:
        playlist_data = {
            "name": name,
            "songs": urls
        }

        file_path = os.path.join(self.path, f"{name}.json")
        with open(file_path, "w") as f:
            json.dump(playlist_data, f, indent=4)

        logger.info(f"Playlist {name} has been created.")

    def read_playlist(self, filename: str) -> None:
        file_path = os.path.join(self.path, filename)
        if not os.path.exists(file_path):
            logger.error(f"Playlist '{filename}' does not exist.")
            return
        
        with open(file_path, "r") as f:
            playlist_data = json.load(f)
        
        playlist = Playlist(playlist_data["name"])
        self.playlists.append(playlist)
        for song in playlist_data["songs"]:
            playlist.add_song(song)
        logger.info(f"Loaded playlist '{playlist_data['name']}' with {len(playlist_data['songs'])} songs.")

    def add_song_to_playlist(self, name: str, url: str) -> None:
        file_path = os.path.join(self.path, f"{name}.json")
        if not os.path.exists(file_path):
            logger.error(f"Playlist '{name}' does not exist.")
            return

        with open(file_path, "r") as f:
            playlist_data = json.load(f)

        playlist_data["songs"].append(url)

        with open(file_path, "w") as f:
            json.dump(playlist_data, f, indent=4)
        logger.info(f"Added song to playlist '{name}': {url}")

    def remove_song_from_playlist(self, name: str, index: int) -> None:
        file_path = os.path.join(self.path, f"{name}.json")
        if not os.path.exists(file_path):
            logger.error(f"Playlist '{name}' does not exist.")
            return

        with open(file_path, "r") as f:
            playlist_data = json.load(f)

        if 0 <= index < len(playlist_data["songs"]):
            removed_song = playlist_data["songs"].pop(index)
            with open(file_path, "w") as f:
                json.dump(playlist_data, f, indent=4)
            logger.info(f"Removed song from playlist '{name}': {removed_song}")
        else:
            logger.error(f"Invalid index {index} for playlist '{name}'.")

    def remove_playlist_json(self, name: str) -> None:
        file_path = os.path.join(self.path, f"{name}.json")
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Playlist '{name}' removed.")
        else:
            logger.error(f"Playlist '{name}' does not exist.")