import json
import re
import threading
import tlc5947
import queue

class command:
    def __init__(self, message):
        self.ledAddr = self.__getLedAddr(message.topic)

        parsedMessage = json.loads(message.payload.decode())

        self.brightness = parsedMessage["brightness"]
        self.transition = parsedMessage["transition"]

    def __getLedAddr(self, topic):
        driverNumber = int(re.search(f"(?<={tlc5947.driverNamePrefix})\\d*", topic).group())
        ledNumber = int(re.search(f"(?<={tlc5947.ledNamePrefix})\\d*", topic).group())

        return driverNumber * ledNumber