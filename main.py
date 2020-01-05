import badgyRev2C
from machine import Pin, SPI

# SPI1 on ESP8266
spi  = SPI(1, baudrate=40000000, polarity=0, phase=0)

# SPI pins for Badgy
cs   = Pin(15, Pin.OUT)
dc   = Pin(0, Pin.OUT)
rst  = Pin(2, Pin.OUT)
busy = Pin(4, Pin.OUT)

e = badgyRev2C.EPD(spi, cs, dc, rst, busy)
e.init()

w = 128
h = 296
x = 0
y = 0

from image import micropython_logo
e.set_frame_memory(micropython_logo, x, y, w, h)
e.display_frame()
