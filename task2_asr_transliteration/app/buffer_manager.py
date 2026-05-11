import queue
import threading
import time

class AudioBufferManager:
    """
    Queue-based buffer to handle chunked audio, prevent overflow,
    and support asynchronous processing.
    """
    def __init__(self, maxsize=100):
        self.audio_queue = queue.Queue(maxsize=maxsize)
        self.is_running = True

    def put_chunk(self, audio_chunk):
        try:
            self.audio_queue.put(audio_chunk, timeout=2)
            return True
        except queue.Full:
            print("Warning: Audio buffer is full. Dropping chunk.")
            return False

    def get_chunk(self):
        try:
            return self.audio_queue.get(timeout=1)
        except queue.Empty:
            return None

    def worker_loop(self, process_callback):
        """
        Continuously pulls from the queue and calls the processing callback.
        """
        while self.is_running:
            chunk = self.get_chunk()
            if chunk is not None:
                process_callback(chunk)
                self.audio_queue.task_done()
            else:
                time.sleep(0.1)

    def stop(self):
        self.is_running = False
