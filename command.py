import environment as env
import json
import re
import threading
import tlc5947
import queue

class command:
    def __init__(self, message):
        try:
            self.ledAddr = self.__getLedAddr(message.topic)
            if (env.logLevel is env.DEBUG and self.ledAddr):
                print(f"Command parsed led addr: {self.ledAddr}")

            if (message.payload is not None):
                parsedMessage = json.loads(message.payload.decode())

                self.state = parsedMessage.get("state")
                if (env.logLevel is env.DEBUG and self.state):
                    print(f"Command parsed state: {self.state}")

                self.brightness = parsedMessage.get("brightness")
                if (env.logLevel is env.DEBUG and self.brightness):
                    print(f"Command parsed brightness: {self.brightness}")

                self.transition = parsedMessage.get("transition")
                if (env.logLevel is env.DEBUG and self.transition):
                    print(f"Command parsed transition: {self.transition}")

                self.effect = parsedMessage.get("effect")
                if (env.logLevel is env.DEBUG and self.effect):
                    print(f"Command parsed effect: {self.effect}")

        except:
            print("Error parsing message")

    def __getLedAddr(self, topic):
        driverNumber = int(re.search(f"(?<={tlc5947.driverNamePrefix})\\d*", topic).group())
        ledNumber = int(re.search(f"(?<={tlc5947.ledNamePrefix})\\d*", topic).group())

        return driverNumber * ledNumber