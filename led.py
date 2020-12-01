import asyncio
import concurrent
import instruction
import time
from threading import Thread

resolution_ms = 10

def start_background_loop(loop: asyncio.AbstractEventLoop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

event_loop = asyncio.new_event_loop()
t = Thread(target=start_background_loop, args=(event_loop,), daemon=True)
t.start()

class led:
    def __init__(self, addr, instructionHandler):
        self.addr = addr
        self.__brightness = 0
        self.__instructionHandler = instructionHandler
        self.__task = None

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

    def fade(self, target_brightness, duration_s):
        duration_ms = 1000 * duration_s
        start_brightness = self.brightness
        steps = max(1, int(duration_ms / resolution_ms))
        brightness_step = round((target_brightness - start_brightness) / steps)
        async def loop():
            i = 1
            while i <= steps:
                self.brightness += brightness_step
                await self.__sleep()
                i += 1
                if (i == steps):
                    self.brightness = target_brightness

        self.__run_loop(loop())

class controller:
    def __init__(self, num_leds, instructionHandler):
        self.__leds = [led(i, instructionHandler) for i in range (num_leds)]

    def handle(self, command):
        led = self.__leds[command.ledAddr]

        led.fade(command.brightness, command.transition)