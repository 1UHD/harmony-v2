import os

from src.tools.Song import Song

class Playlist:

    def __init__(self, name: str) -> None:
        self.name = name
        self.songs = []
        self.length = None
        self.song_amount = 0

class PlaylistUtility:

    def __init__(self) -> None:
        self.path = __file__.replace("/src/tools/Playlist.py", "/playlists/")
        self.playlists = []

    def _initialize_filepath(self) -> None:
        ...

    def _get_all_playlists(self) -> None:
        path = os.fsencode(self.path)

        for file in os.listdir(path):
            os.fsdecode(file)

            


    def create(self, name: str) -> None:
        playlist = Playlist(name=name)
        playlist.songs = self._get_songs_from_file()
        self.playlists.append(playlist)