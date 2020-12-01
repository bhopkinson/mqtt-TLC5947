import threading
import queue

class handler():
    def __init__(self):
        self.queue = queue.Queue(maxsize=0)

    def loop_start(self):
        def loopInternal():
            while True:
                item = self.queue.get()
                if (self.callback):
                    self.callback(item)

        self.thread = threading.Thread(target=loopInternal)
        self.thread.start()

    def handle(self, item):
        self.queue.put(item)

    def set_callback(self, callback):
        self.callback = callback