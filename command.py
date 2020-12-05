import json
import re
import threading
import tlc5947
import queue

class command:
    def __init__(self, message):
        self.ledAddr = self.__getLedAddr(message.topic)

        if (message.payload is not None):
            try:
                parsedMessage = json.loads(message.payload.decode())
                self.state = parsedMessage.get("state")
                self.brightness = parsedMessage.get("brightness")
                self.transition = parsedMessage.get("transition")
            except:
                print("Error parsing message")

    def __getLedAddr(self, topic):
        driverNumber = int(re.search(f"(?<={tlc5947.driverNamePrefix})\\d*", topic).group())
        ledNumber = int(re.search(f"(?<={tlc5947.ledNamePrefix})\\d*", topic).group())

        return driverNumber * ledNumber