import src.tools.Song as Song

class Queue:

    def __init__(self) -> None:
        self.queue = []

    def add(self, song: Song.Song) -> None:
        self.queue.append(song)

    def get_first_song(self) -> Song.Song:
        return self.queue[0]
    
    def clear(self) -> None:
        self.queue.clear()

    def remove(self, index: int) -> None:
        self.queue.pop(index)