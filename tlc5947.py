#import datetime
# import adafruit_tlc5947
# import board
# import busio
# import digitalio
import environment as env
import math

numberOfLeds = 24

def getBoardNumber(addr):
    return math.ceil(addr / numberOfLeds)

def getLedNumber(addr):
    boardNumber = getBoardNumber(addr)
    return addr - ((boardNumber - 1) * numberOfLeds)

class tlc5947:
    def __init__(self):
        self.numberOfLeds = env.driverCount * numberOfLeds
        
        # spi = busio.SPI(board.SCLK, board.MOSI, board.MISO)
        # latch = digitalio.DigitalInOut(board.D4)
        # self.tlc5947 = adafruit_tlc5947.TLC5947(spi, latch, num_drivers=driverCount)

    def handle(self, instruction):
        print(f"{instruction.addr}: {instruction.pwm}")
        #self.tlc5947[instruction.addr] = instruction.pwm