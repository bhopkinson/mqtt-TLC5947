#import datetime
import adafruit_tlc5947
import board
import busio
import digitalio
import environment as env
import math

numberOfLeds = 24

driverNamePrefix = "driver-"
ledNamePrefix = "led-"

def getDriverNumber(addr):
    test = max(math.ceil(addr / numberOfLeds), 1)
    return test

def getDriverName(driverNumber):
    return f"{driverNamePrefix}{driverNumber}"

def getLedNumber(addr):
    driverNumber = getDriverNumber(addr)
    return addr - ((driverNumber - 1) * numberOfLeds)

def getLedName(ledNumber):
    return f"{ledNamePrefix}{ledNumber}"

class tlc5947:
    def __init__(self):
        self.tlc5947 = None
        self.numberOfLeds = env.driverCount * numberOfLeds

        if (env.latchPin):
            spi = busio.SPI(board.SCLK, board.MOSI, board.MISO)
            latch = digitalio.DigitalInOut(getattr(board, env.latchPin))
            self.tlc5947 = adafruit_tlc5947.TLC5947(spi, latch, num_drivers=env.driverCount)

    def handle(self, instruction):
        print(f"{instruction.addr}: {instruction.pwm}")
        if (self.tlc5947):
            self.tlc5947[instruction.addr] = instruction.pwm