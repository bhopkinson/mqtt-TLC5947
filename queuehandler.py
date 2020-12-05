import environment as env
import threading
import queue

class handler():
    def __init__(self):
        self.queue = queue.Queue(maxsize=0)

    def loop_start(self):
        def loopInternal():
            while True:
                if (env.logLevel == env.DEBUG):
                    print(f"Queue loop: {self}")
                item = self.queue.get()
                if (env.logLevel == env.DEBUG):
                    print(f"Got queue item: {item}")
                if (self.callback):
                    self.callback(item)

        self.thread = threading.Thread(target=loopInternal)
        self.thread.start()

    def handle(self, item):
        if (env.logLevel == env.DEBUG):
            print(f"Handling item: {item}")
        self.queue.put(item)

    def set_callback(self, callback):
        self.callback = callback