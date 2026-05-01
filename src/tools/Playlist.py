import os
import json
import time
import asyncio

from src.tools.Song import Song
from src.tools.logging import logger
from src.tools.Queue import queue
from src.tools.YoutubeHelper import yt_helper

class Playlist:

    def __init__(self, name: str) -> None:
        self.name = name
        self.songs = []
        self.length = None
        self.song_amount = len(self.songs)

    def get_song_amount(self) -> int:
        return len(self.songs)

    def add_song(self, song: Song) -> None:
        self.songs.append(song)

    def remove_song(self, index: str) -> None:
        self.songs.pop(index)

    async def get_formatted(self) -> str:
        start_time = time.time()
        titles = await asyncio.gather(
            *(yt_helper.get_yt_title(song) for song in self.songs)
        )
        result = [f"{i + 1}. {title}" for i, title in enumerate(titles)]
        
        logger.debug(f"done (took {time.time() - start_time}s)")
        return "\n".join(result)


class PlaylistUtilityCsv:
    
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
                if file.endswith(".csv"):
                    playlist_files.append(file)

        except Exception as e:
            logger.error("Coudln't load playlists.", True)
            logger.error(e)
            return
        
        return playlist_files

    #format: url,title,artist,artist_subs,thumbnail,views,likes,upload_date,length,is_restricted,audio_url
    def _song_to_csv_format(self, s: Song) -> str:
        return f"{s.url},{s.title},{s.artist},{s.artist_subs},{s.thumbnail},{s.views},{s.likes},{s.upload_date},{s.length},{s.is_restricted},{s.audio_url}\n"

    def _convert_to_int(self, value: str) -> int | None:
        try:
            return int(value)
        except:
            logger.warning(f"Couldnt parse value {value} during csv conversion")
            return None

    def _csv_format_to_song(self, line: str) -> Song:
        c = line.split(",")

        s = Song(url=c[0])
        s.title = c[1]
        s.artist = c[2]
        s.artist_subs = self._convert_to_int(c[3])
        s.thumbnail = c[4]
        s.views = self._convert_to_int(c[5])
        s.likes = self._convert_to_int(c[6])
        s.upload_date = c[7]
        s.length = self._convert_to_int(c[8])
        s.is_restricted = True if c[9] == "True" else False
        s.audio_url = c[10]
        s.use_audio_url()

        return s

    def _get_playlist_object_by_name(self, name: str) -> Playlist | None:
        for pl in self.playlists:
            if pl.name == name:
                return pl

        return None

    def write_playlist(self, name: str, songs: list[Song]) -> None:
        playlist_path = os.path.join(self.path, f"{name}.csv")
        playlist_header = name
        playlist_songs = "".join(self._song_to_csv_format(s) for s in songs) if len(songs) > 0 else ""
        data = playlist_header + "\n" + playlist_songs

        with open(playlist_path, "w") as f:
            f.write(data)

        logger.info(f"Wrote playlist csv for {name}")

    #first line: playlist header, x after that songs in playlist
    def read_playlist(self, filename: str) -> None:
        file_path = os.path.join(self.path, filename)
        if not os.path.exists(file_path):
            logger.error(f"Playlist '{filename}' does not exist.")
            return

        with open(file_path, "r") as f:
            playlist_data = f.read()

        playlist_members = playlist_data.split("\n")
        playlist_header = playlist_members[0]
        playlist_songs = playlist_members[1:]

        playlist_headers = playlist_header.split(",")
        pl = Playlist(name=playlist_headers[0])
        self.playlists.append(pl)

        for song in playlist_songs:
            if len(song) > 0:
                pl.songs.append(self._csv_format_to_song(song))

        logger.info(f"Loaded playlists {pl.name} with {pl.song_amount} songs")

    def is_available(self, name: str) -> bool:
        for p in self.playlists:
            if p.name == name:
                return False
        
        return True

    def save_playlist(self, pl: Playlist) -> None:
        self.write_playlist(name=pl.name, songs=pl.songs)

    def create_playlist(self, name: str) -> None:
        if self.is_available(name):
            pl = Playlist(name)
            self.playlists.append(pl)
            self.save_playlist(pl)

    def remove_playlist(self, pl: Playlist) -> None:
        playlist_path = os.path.join(self.path, f"{pl.name}.csv")

        if os.path.exists(playlist_path):
            os.remove(playlist_path)
        else:
            logger.warning(f"Path for {pl.name} doesnt exist")

    def add_song(self, song: Song, pl: Playlist) -> None:
        pl.add_song(song=song)
        self.save_playlist(pl)

    def remove_song(self, pl: Playlist, index: int) -> None:
        if index > 0 and index <= pl.song_amount:
            pl.songs.pop(index-1)



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
        
    def _create_playlist_json(self, name: str, urls: list[str]) -> None:
        playlist_data = {
            "name": name,
            "songs": urls
        }

        file_path = os.path.join(self.path, f"{name}.json")
        with open(file_path, "w") as f:
            json.dump(playlist_data, f, indent=4)

        logger.info(f"Playlist json for {name} has been created.")

    def check_playlist_name_availability(self, name: str) -> bool:
        for playlist in self.playlists:
            if name.lower() == playlist.name.lower():
                return False
            
        return True
    
    def check_playlist_existence(self, name: str) -> bool:
        for playlist in self.playlists:
            if name.lower() == playlist.name.lower():
                return True
            
        return False
    
    def find_playlist_object_by_name(self, name: str) -> Playlist:
        for playlist in self.playlists:
            if name.lower() == playlist.name.lower():
                return playlist

    def queue_playlist(self, playlist: Playlist) -> None:
        for url in playlist.songs:
            song = Song(url=url)
            queue.add(song=song)

    def create_playlist(self, name: str) -> None:
        playlist = Playlist(name=name)
        self.playlists.append(playlist)
        self._create_playlist_json(name=name, urls=[])

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

    def add_song_to_playlist(self, playlist: str, url: str) -> None:
        name = self.find_playlist_object_by_name(name=playlist).name

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

    def remove_song_from_playlist(self, playlist: str, index: int) -> None:
        name = self.find_playlist_object_by_name(name=playlist).name

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

    def remove_playlist_json(self, playlist: str) -> None:
        name = self.find_playlist_object_by_name(name=playlist).name

        file_path = os.path.join(self.path, f"{name}.json")
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Playlist '{name}' removed.")
        else:
            logger.error(f"Playlist '{name}' does not exist.")

PlaylistManager = PlaylistUtility()
playlist_manager = PlaylistUtilityCsv()