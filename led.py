import asyncio
import concurrent
import discovery
import environment as env
import instruction
import time
from threading import Thread
import tlc5947

resolution_ms = 15

def start_background_loop(loop: asyncio.AbstractEventLoop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

event_loop = asyncio.new_event_loop()
t = Thread(target=start_background_loop, args=(event_loop,), daemon=True)
t.start()

mqtt = None

class led:
    def __init__(self, addr, instructionHandler):
        self.addr = addr
        self.storedBrightness = 4095
        self.__internalBrightness = 0
        self.__target_brightness = 0
        self.__instructionHandler = instructionHandler
        self.__task = None

        self.__driverNum = tlc5947.getDriverNumber(self.addr)
        self.__driverName = tlc5947.getDriverName(self.__driverNum)
        self.__ledNum = tlc5947.getLedNumber(self.addr)
        self.__ledName = tlc5947.getLedName(self.__ledNum)

        self.__subTopic = f"{self.__driverName}/{self.__ledName}"
        self.__stateTopic = f"{self.__subTopic}/state"
        self.__uniqueId = f"{self.__driverName}_{self.__ledName}"

        if (env.discoveryTopic):
            self.sendDiscovery()

        self.publishState()

    async def __sleep(self):
        await asyncio.sleep(resolution_ms / 1000)

    def __run_loop(self, loop):
        if (self.__task is not None): self.__task.cancel()
        self.__task = asyncio.run_coroutine_threadsafe(loop, event_loop)

    # @property
    # def brightness(self):
    #     return self.__internalBrightness

    # @brightness.setter
    # def brightness(self, brightness):
    #     self.__internalBrightness = brightness
    #     self.__instructionHandler.handle(instruction.instruction(self.addr, brightness))

    def __set_internalBrightness(self, brightness):
        if (brightness > 4095):
            print (f"Brightness value of {brightness} is greater than max allowed 4095.")
            return

        self.__internalBrightness = brightness
        self.__instructionHandler.handle(instruction.instruction(self.addr, brightness))

    def sendDiscovery(self):
        message = {
            discovery.command_topic: f"~/{self.__subTopic}/set",
            discovery.state_topic: f"~/{self.__stateTopic}",
            discovery.schema: "json",
            discovery.brightness: True,
            discovery.brightness_scale: 4095,
            discovery.effect: True,
            discovery.effect_list: ["fire_flicker", "spark"]
        }
        mqtt.send_discovery_message(message, self.__uniqueId, discovery.light)

    def publishState(self):
        if (self.__target_brightness):
            state = "ON"
        else:
            state = "OFF"

        message = {
            "state": state,
            "brightness": self.storedBrightness
        }

        mqtt.publish(self.__stateTopic, message)

    def fade(self, target_brightness, duration_s):
        self.__target_brightness = target_brightness
        start_brightness = self.__internalBrightness
        start_time = time.perf_counter()
        brightness_diff = target_brightness - start_brightness
        async def loop():
            while self.__internalBrightness != target_brightness:
                elapsed = time.perf_counter() - start_time
                new_brightness = start_brightness + round(brightness_diff * min(elapsed, duration_s) / duration_s)
                if (elapsed >= duration_s):
                    new_brightness = target_brightness
                self.__set_internalBrightness(new_brightness)
                await self.__sleep()

        self.__run_loop(loop())

class controller:
    def __init__(self, num_leds, instructionHandler):
        self.__leds = [led(i, instructionHandler) for i in range (num_leds)]

    def handle(self, command):
        if (command.ledAddr >= len(self.__leds)):
            print(f"Error: led address {command.ledAddr} out of bounds. Max address {len(self.__leds) - 1}")
            return

        led = self.__leds[command.ledAddr]

        transition = 0
        if (command.transition):
            transition = command.transition

        if (command.state == 'ON'):
            if (command.brightness is not None):
                led.storedBrightness = command.brightness
            led.fade(led.storedBrightness, transition)
        else:
            led.fade(0, transition)

        led.publishState()