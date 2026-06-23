from pathlib import Path
import tidalapi
import src.settings as settings
from tidalapi.album import Album
from tidalapi.media import Media, Track
from tidalapi.session import SearchResults, StreamNotAvailable

from src.tools.logging import logger

class TidalHelper:
    def __init__(self):
        if settings.tidal:
            session_file = Path("tidal-session-oauthn.json")
            session = tidalapi.Session()
            if not session.login_session_file(session_file):
                logger.error("Failed to authenticate tidal")
            self.session = session

    def query(self, query: str, limit:int=1, types = [Track]) -> SearchResults:
        results = self.session.search(query, types, limit=limit)
        return results

    def get_track(self, track_id: str) -> tidalapi.Track:
        return self.session.track(track_id)

    def get_link(self, track: tidalapi.Track) -> str:
        stream = track.get_stream()
        manifest = stream.get_stream_manifest()
        if manifest.is_mpd:
            url = manifest.get_hls()
        else:
            url = manifest.get_urls()[0]
        return url
    
tidal_helper = TidalHelper()
