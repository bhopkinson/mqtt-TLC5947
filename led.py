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
        self.__brightness = 0
        self.__instructionHandler = instructionHandler
        self.__task = None

        if (env.discoveryTopic):
            self.sendDiscovery()

    async def __sleep(self):
        await asyncio.sleep(resolution_ms / 1000)

    def __run_loop(self, loop):
        if (self.__task is not None): self.__task.cancel()
        self.__task = asyncio.run_coroutine_threadsafe(loop, event_loop)

    @property
    def brightness(self):
        return self.__brightness

    @brightness.setter
    def brightness(self, brightness):
        self.__brightness = brightness
        self.__instructionHandler.handle(instruction.instruction(self.addr, brightness))

    def sendDiscovery(self):
        boardNum = tlc5947.getBoardNumber(self.addr)
        ledNum = tlc5947.getLedNumber(self.addr)
        subTopic = f"board-{boardNum}/led-{ledNum}"
        uniqueId = f"board-{boardNum}_led-{ledNum}"
        message = {
            discovery.command_topic: "~/set",
            discovery.schema: "json",
            discovery.brightness: True
        }
        mqtt.send_discovery_message(message, subTopic, uniqueId, discovery.light)

    def fade(self, target_brightness, duration_s):
        start_brightness = self.brightness
        start_time = time.perf_counter()
        brightness_diff = target_brightness - self.brightness
        async def loop():
            while self.brightness != target_brightness:
                elapsed = time.perf_counter() - start_time
                new_brightness = start_brightness + round(brightness_diff * min(elapsed, duration_s))
                if (elapsed >= duration_s):
                    new_brightness = target_brightness
                self.brightness = new_brightness
                await self.__sleep()

        self.__run_loop(loop())

class controller:
    def __init__(self, num_leds, instructionHandler):
        self.__leds = [led(i, instructionHandler) for i in range (num_leds)]

    def handle(self, command):
        led = self.__leds[command.ledAddr - 1]

        led.fade(command.brightness, command.transition)