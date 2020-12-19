import asyncio
import concurrent
import discovery
import environment as env
import instruction
import random
import time
from threading import Thread
import tlc5947

resolution_ms = 15
max_brightness = 4095

def start_background_loop(loop: asyncio.AbstractEventLoop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

event_loop = asyncio.new_event_loop()
t = Thread(target=start_background_loop, args=(event_loop,), daemon=True)
t.start()

mqtt = None

effect_none = "None"
effect_fire_flicker = "Fire flicker"
effect_street_light_flicker = "Street light flicker"
effect_welding_spark = "Welding spark"

class led:
    def __init__(self, addr, instructionHandler):
        self.addr = addr
        self.storedBrightness = max_brightness
        self.effect = effect_none
        self.__target_brightness = 0
        self.__instructionHandler = instructionHandler
        self.__task = None

        self.__set_internalBrightness(0)

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
        if (self.__task is not None):
            self.__task.cancel()

        self.__task = asyncio.run_coroutine_threadsafe(loop, event_loop)

    def __set_internalBrightness(self, brightness):
        if (env.logLevel == env.DEBUG):
            print (f"__set_internalBrightness: {brightness}")

        if (brightness > max_brightness):
            print (f"Brightness value of {brightness} is greater than max allowed {max_brightness}.")
            return

        self.__internalBrightness = brightness
        self.__instructionHandler.handle(instruction.instruction(self.addr, brightness))

    def sendDiscovery(self):
        message = {
            discovery.command_topic: f"~/{self.__subTopic}/set",
            discovery.state_topic: f"~/{self.__stateTopic}",
            discovery.schema: "json",
            discovery.brightness: True,
            discovery.brightness_scale: max_brightness,
            discovery.effect: True,
            discovery.effect_list: [effect_none, effect_fire_flicker, effect_street_light_flicker, effect_welding_spark]
        }
        mqtt.send_discovery_message(message, self.__uniqueId, discovery.light)

    def publishState(self):
        if (self.__target_brightness):
            state = "ON"
        else:
            state = "OFF"

        message = {
            "state": state,
            "brightness": self.storedBrightness,
            "effect": self.effect
        }

        mqtt.publish(self.__stateTopic, message)

    def fade(self, target_brightness, duration_s):
        if (env.logLevel == env.DEBUG):
            print(f"fade: target: {target_brightness}, duration: {duration_s}")

        self.__target_brightness = target_brightness
        start_brightness = self.__internalBrightness
        start_time = time.perf_counter()
        brightness_diff = target_brightness - start_brightness
        async def loop():
            if (env.logLevel == env.DEBUG):
                print(f"Begin led {self.addr} loop")

            while self.__internalBrightness != target_brightness:
                try:
                    if (env.logLevel == env.DEBUG):
                        print(f"Led {self.addr} loop")

                    elapsed = time.perf_counter() - start_time

                    if (elapsed >= duration_s or duration_s == 0):
                        new_brightness = target_brightness
                    else:
                        new_brightness = start_brightness + round(brightness_diff * min(elapsed, duration_s) / duration_s)

                    self.__set_internalBrightness(new_brightness)
                    await self.__sleep()

                except Exception as e:
                    print(f"Exception in led {self.addr} fade loop: {e}")
                    break


        self.__run_loop(loop())

    def fire_flicker(self, brightness):
        self.storedBrightness = brightness or self.storedBrightness
        self.__target_brightness = self.storedBrightness
        min_brightness = max(500, self.storedBrightness - 2750)
        async def loop():
            try:
                while True:
                    new_brightness = random.randint(min(min_brightness, self.storedBrightness), max(min_brightness, self.storedBrightness))
                    delay = random.randint(10, 100) / 1000
                    if (env.logLevel == env.DEBUG):
                        print(f"Led {self.addr} fire flicker: brightness: {new_brightness}, delay: {delay}")
                    self.__set_internalBrightness(new_brightness)
                    await asyncio.sleep(delay)
            except Exception as e:
                print(f"Exception in led {self.addr} fire_flicker loop: {e}")

        self.__run_loop(loop())

    def street_light_flicker(self, brightness):
        self.storedBrightness = brightness or self.storedBrightness
        self.__target_brightness = self.storedBrightness
        async def loop():
            try:
                while True:
                    wide_range_brightness = random.randint(0 - self.storedBrightness - 750, self.storedBrightness + 750) # use wide range to add weighting to min and max values
                    new_brightness = min(max(0, wide_range_brightness), self.storedBrightness)
                    self.__set_internalBrightness(new_brightness)
                    await asyncio.sleep(random.randint(80, 500) / 1000)
            except Exception as e:
                print(f"Exception in led {self.addr} street_light_flicker loop: {e}")

        self.__run_loop(loop())

    def welding_spark(self, brightness):
        self.storedBrightness = brightness or self.storedBrightness
        self.__target_brightness = self.storedBrightness
        spark_probability = 0.05
        async def loop():
            try:
                while True:
                    if (random.random() <= spark_probability):
                        new_brightness = random.randint(3000, max_brightness)
                        delay_ms = random.randint(10, 200)
                    else:
                        low_brightness = max(self.storedBrightness - 225, 0)
                        high_brightness = min(self.storedBrightness + 225, max_brightness)
                        new_brightness = random.randint(low_brightness, high_brightness)
                        delay_ms = random.randint(5, 55)
                    self.__set_internalBrightness(new_brightness)
                    await asyncio.sleep(delay_ms / 1000)
            except Exception as e:
                print(f"Exception in led {self.addr} spark loop: {e}")
        
        self.__run_loop(loop())

class controller:
    def __init__(self, num_leds, instructionHandler):
        self.__leds = [led(i, instructionHandler) for i in range (num_leds)]

    def handle(self, command):
        try:
            if (command.ledAddr >= len(self.__leds)):
                print(f"Error: led address {command.ledAddr} out of bounds. Max address {len(self.__leds) - 1}")
                return

            led = self.__leds[command.ledAddr]

            if (env.logLevel == env.DEBUG):
                print(f"LED: {led.addr}")

            transition = 0
            if (command.transition):
                transition = command.transition

            if (env.logLevel == env.DEBUG):
                print(f"transition: {transition}")

            if (command.state == 'OFF' or command.brightness == 0):
                led.fade(0, transition)
            else:
                if (command.effect):
                    led.effect = command.effect 

                if (led.effect == effect_none):

                    if (command.brightness is not None):
                        led.storedBrightness = command.brightness

                    led.fade(led.storedBrightness, transition)

                elif (led.effect == effect_fire_flicker):
                    led.fire_flicker(command.brightness)
                elif (led.effect == effect_street_light_flicker):
                    led.street_light_flicker(command.brightness)
                elif (led.effect == effect_welding_spark):
                    led.welding_spark(command.brightness)

        except Exception as e:
            print(f"Exception while handling command {command}: {e}")
        finally:
            try:
                led.publishState()
            except Exception as e:
                print(f"Exception while publishing state for led {led.addr}: {e}")
