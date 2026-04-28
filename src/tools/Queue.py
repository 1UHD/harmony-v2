from src.tools.logging import logger
import src.tools.Song as Song
import asyncio

class Queue:

    def __init__(self) -> None:
        self.queue = []
        self.current = None
        self.current_index = 0
        self.preloaded_songs = 2

        self.paused = False
        self.looped = False
    
    def load_current_song(self) -> None:
        if not self.queue[self.current_index].audio:
            logger.debug(f"getting audio for current index ({self.current_index})")
            self.queue[self.current_index].get_audio()

    def load_song(self, index: int) -> None:
        if index >= len(self.queue):
            logger.warning(f"list index out of range. queue len: {len(self.queue)}, requested index: {index}")
            return

        if not self.queue[index].audio:
            logger.debug(f"getting audio for current index ({index})")
            self.queue[index].get_audio()

    async def load_songs(self) -> None:
        for i in range(self.preloaded_songs):
            if (self.current_index + i + 1) < len(self.queue):
                if not self.queue[self.current_index+i+1].audio:
                    logger.debug(f"getting audio for queue index {self.current_index+i+1}")
                    asyncio.create_task(asyncio.to_thread(self.queue[self.current_index+i+1].get_audio))

    def add(self, song: Song.Song) -> None:
        self.queue.append(song)

    def get_song(self, index: int) -> Song.Song:
        return self.queue[index]
    
    def clear(self) -> None:
        self.queue.clear()

    def remove(self, index: int) -> None:
        self.queue.pop(index)

    def get_length(self) -> int:
        return len(self.queue) - self.current_index
    
    def get_duration(self) -> int:
        remaining = 0

        for song in range(self.current_index, len(self.queue) - 1):
            remaining += self.queue[song].length

        return remaining
    
    def get_formatted(self) -> str:
        result = []
    
        for i, song in enumerate(self.queue):
            if i == self.current_index - 1:
                highlighted_song = f"{i + 1}. **{song.title}**"

                if queue.is_looped():
                    highlighted_song += " (looped)"

                result.append(highlighted_song)
            else:
                result.append(f"{i + 1}. {song.title}")
        
        return "\n".join(result)
    
    def pause(self) -> None:
        self.paused = True

    def unpause(self) -> None:
        self.paused = False

    def is_paused(self) -> bool:
        return self.paused
    
    def loop(self) -> None:
        self.current_index -= 1
        self.looped = True

    def unloop(self) -> None:
        self.current_index += 1
        self.looped = False

    def is_looped(self) -> bool:
        return self.looped
    
    def get_current(self) -> Song.Song:
        return self.current
    
    def set_current(self, song: Song.Song |  None) -> None:
        self.current = song

    def get_current_index(self) -> int:
        return self.current_index
    
    def set_current_index(self, index: int) -> None:
        self.current_index = index

queue = Queue()