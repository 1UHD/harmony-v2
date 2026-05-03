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
                if file.endswith(".json"):
                    playlist_files.append(file)

        except Exception as e:
            logger.error("Coudln't load playlists.", True)
            logger.error(e)
            return
        
        return playlist_files

    def _song_to_json(self, s: song) -> dict:
        return {
            "url": s.url,
            "title": s.title,
            "artist": s.artist,
            "artist_subs": s.artist_subs,
            "thumbnail": s.thumbnail,
            "views": s.views,
            "likes": s.likes,
            "upload_date": s.upload_date,
            "length": s.length,
            "is_restricted": s.is_restricted,
            "audio_url": s.audio_url
        }

    def _json_to_song(self, j: dict) -> Song:
        s = Song(url=j["url"])
        s.title = j["title"]
        s.artist = j["artist"]
        s.artist_subs = j["artist_subs"]
        s.thumbnail = j["thumbnail"]
        s.views = j["views"]
        s.likes = j["likes"]
        s.upload_date = j["upload_date"]
        s.length = j["length"]
        s.is_restricted = j["is_restricted"]
        s.audio_url = j["audio_url"]
        #s.use_audio_url() #unfortunately youtube changes this so we need to refetch it

        return s

    def get_playlist_object_by_name(self, name: str) -> Playlist | None:
        for pl in self.playlists:
            if pl.name == name:
                return pl

        return None

    def write_playlist(self, name: str, songs: list[Song]) -> None:
        playlist_path = os.path.join(self.path, f"{name}.json")
        playlist_songs = []

        for s in songs:
            playlist_songs.append(self._song_to_json(s))

        data = {
            "type": "harmony_v2_playlist_v2",
            "name": name,
            "songs": playlist_songs
        }

        with open(playlist_path, "w") as f:
            f.write(json.dumps(data, indent=4))

        logger.info(f"Wrote playlist json for {name}")

    def read_playlist(self, filename: str) -> None:
        file_path = os.path.join(self.path, filename)
        if not os.path.exists(file_path):
            logger.error(f"Playlist '{filename}' does not exist.")
            return

        with open(file_path, "r") as f:
            playlist_data_string = f.read()

        playlist_data = json.loads(playlist_data_string)

        try:
            header = playlist_data["type"]

            if header != "harmony_v2_playlist_v2":
                logger.error(f"cant load playlist {filename}: unknown playlist type")
                return
        except:
            logger.error(f"Can't load playlist {filename}: outdated playlist")
            return

        playlist_songs = playlist_data["songs"]

        pl = Playlist(name=playlist_data["name"])
        self.playlists.append(pl)

        for song in playlist_songs:
            pl.songs.append(self._json_to_song(song))

        if len(pl.songs) > 0:
            pl.songs[0].get_audio()

        logger.info(f"Loaded playlist {pl.name} with {len(pl.songs)} songs")

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
        playlist_path = os.path.join(self.path, f"{pl.name}.json")

        if os.path.exists(playlist_path):
            os.remove(playlist_path)
            logger.info(f"Removed {pl.name}")
            self.playlists.remove(pl)
        else:
            logger.warning(f"Path for {pl.name} doesnt exist")

    def add_song(self, song: Song, pl: Playlist) -> None:
        pl.add_song(song=song)
        self.save_playlist(pl)

    def remove_song(self, pl: Playlist, index: int) -> None:
        if index > 0 and index <= len(pl.songs):
            logger.debug(f"removing song at index {index-1} of {pl.name}")
            pl.songs.pop(index-1)

        self.save_playlist(pl)

    def queue(self, pl: Playlist) -> None:
        if pl.get_song_amount() < 1:
            logger.warning("cant queue a playlist with 0 songs, aborting")
            return

        for s in pl.songs:
            queue.add(song=s)


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

#PlaylistManager = PlaylistUtility()
playlist_manager = PlaylistUtilityCsv()