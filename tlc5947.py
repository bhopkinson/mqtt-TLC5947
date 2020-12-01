# import adafruit_tlc5947
# import board
# import busio
# import digitalio

class tlc5947:
    def __init__(self, driverCount):
        self.numberOfLeds = driverCount * 24
        
        # spi = busio.SPI(board.SCLK, board.MOSI, board.MISO)
        # latch = digitalio.DigitalInOut(board.D4)
        # self.tlc5947 = adafruit_tlc5947.TLC5947(spi, latch, num_drivers=driverCount)

    def handle(self, instruction):
        print(f"{instruction.addr}: {instruction.pwm}")
        #self.tlc5947[instruction.addr] = instruction.pwm