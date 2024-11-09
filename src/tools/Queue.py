import src.tools.Song as Song

class Queue:

    def __init__(self) -> None:
        self.queue = []
        self.current = None

        self.paused = False
        self.looped = False

    def add(self, song: Song.Song) -> None:
        self.queue.append(song)

    def get_first_song(self) -> Song.Song:
        return self.queue[0]
    
    def clear(self) -> None:
        self.queue.clear()

    def remove(self, index: int) -> None:
        self.queue.pop(index)

    def get_length(self) -> int:
        return len(self.queue)
    
    def pause(self) -> None:
        self.paused = True

    def unpause(self) -> None:
        self.paused = False

    def is_paused(self) -> bool:
        return self.paused
    
    def loop(self) -> None:
        self.looped = True

    def unloop(self) -> None:
        self.looped = False

    def is_looped(self) -> bool:
        return self.looped
    
    def get_current(self) -> Song.Song:
        return self.current
    
    def set_current(self, song: Song.Song | None) -> None:
        self.current = song
    

queue = Queue()