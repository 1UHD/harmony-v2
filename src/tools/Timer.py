import time
from src.tools.Queue import Queue

class Timer:
    
    def __init__(self) -> None:
        self.song_started = 0
        self.time_elapsed = 0

    def start(self) -> None:
        self.clear()
        self.song_started = time.time()

    def pause(self) -> None:
        self.time_elapsed = time.time() - self.song_started

    def unpause(self) -> None:
        self.song_started = time.time()

    def clear(self) -> None:
        self.song_started = 0
        self.time_elapsed = 0

    def get_time_elapsed(self) -> None:
        if Queue.is_paused():
            return self.time_elapsed
        else:
            return self.time_elapsed + (time.time() - self.song_started)
        
timer = Timer()