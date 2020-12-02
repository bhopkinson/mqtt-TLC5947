import json
import re
import threading
import queue

class command:
    def __init__(self, message):
        self.ledAddr = self.__getLedAddr(message.topic)

        parsedMessage = json.loads(message.payload.decode())

        self.brightness = parsedMessage["brightness"]
        self.transition = parsedMessage["transition"]

    def __getLedAddr(self, topic):
        boardNumber = int(re.search(r"(?<=driver-)\d*", topic).group())
        ledNumber = int(re.search(r"(?<=led-)\d*", topic).group())

        return boardNumber * ledNumber