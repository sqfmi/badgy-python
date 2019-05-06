import epaper2in9
from machine import Pin, SPI

# SPI1 on ESP8266
spi  = SPI(1, baudrate=80000000, polarity=0, phase=0)

# SPI pins for Badgy
cs   = Pin(15, Pin.OUT)
dc   = Pin(0, Pin.OUT)
rst  = Pin(2, Pin.OUT)
busy = Pin(4, Pin.OUT)

e = epaper2in9.EPD(spi, cs, dc, rst, busy)
e.init()

w = 128
h = 296
x = 0
y = 0

import framebuf

def print():
	e.clear_frame_memory(0xFF)
	e.display_frame()
	buf = bytearray(128 * 296 // 8)
	fb = framebuf.FrameBuffer(buf, 128, 296, framebuf.MONO_HLSB)
	black = 0
	white = 1
	fb.fill(white)
	fb.text('Hello',44,0,black)
	fb.text('my name is',24,8,black)
	fb.text('badgy',44,16,black)
	fb.pixel(64, 24, black)
	fb.hline(32, 32, 64, black)
	fb.vline(64, 40, 64, black)
	fb.line(30, 70, 40, 80, black)
	fb.rect(32, 112, 10, 10, black)
	fb.fill_rect(32, 130, 10, 10, black)
	e.set_frame_memory(buf, x, y, w, h)
	e.display_frame()