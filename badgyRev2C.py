from micropython import const
from time import sleep_ms

# Display resolution
EPD_WIDTH  = const(128)
EPD_HEIGHT = const(296)

BUSY = const(1)  # 1=busy\=idle

class EPD:
    def __init__(self, spi, cs, dc, rst, busy):
        self.spi = spi
        self.cs = cs
        self.dc = dc
        self.rst = rst
        self.busy = busy
        self.cs.init(self.cs.OUT, value=1)
        self.dc.init(self.dc.OUT, value=0)
        self.rst.init(self.rst.OUT, value=0)
        self.busy.init(self.busy.IN)
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT

    LUT_20_VCOMDC = bytearray(b'\x00\x08\x00\x00\x00\x02\x60\x28\x28\x00\x00\x01\x00\x14\x00\x00\x00\x01\x00\x12\x12\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
    LUT_21_WW = bytearray(b'\x40\x08\x00\x00\x00\x02\x90\x28\x28\x00\x00\x01\x40\x14\x00\x00\x00\x01\xA0\x12\x12\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
    LUT_22_BW = bytearray(b'\x40\x08\x00\x00\x00\x02\x90\x28\x28\x00\x00\x01\x40\x14\x00\x00\x00\x01\xA0\x12\x12\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
    LUT_23_WB = bytearray(b'\x80\x08\x00\x00\x00\x02\x90\x28\x28\x00\x00\x01\x80\x14\x00\x00\x00\x01\x50\x12\x12\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
    LUT_24_BB = bytearray(b'\x80\x08\x00\x00\x00\x02\x90\x28\x28\x00\x00\x01\x80\x14\x00\x00\x00\x01\x50\x12\x12\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')

    def _command(self, command, data=None):
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([command]))
        self.cs(1)
        if data is not None:
            self._data(data)

    def _data(self, data):
        self.dc(1)
        self.cs(0)
        self.spi.write(data)
        self.cs(1)

    def init(self):
        self.reset()

    def wait_until_idle(self):
        while self.busy.value() == BUSY:
            sleep_ms(100)

    def reset(self):
        self.rst(0)
        sleep_ms(200)
        self.rst(1)
        sleep_ms(200)

    # put an image in the frame memory
    def set_frame_memory(self, image, x, y, w, h):
        self.clear_frame_memory(0xFF)
        self._command(0x13, image)

    # replace the frame memory with the specified color
    def clear_frame_memory(self, color):
        self._wake_up()
        self._command(0x10)
        # send the color data
        for i in range(0, self.width // 8 * self.height):
            self._data(bytearray([color]))

    # draw the current frame memory and switch to the next memory area
    def display_frame(self):
        self._command(0x12)
        self.wait_until_idle()
        self._sleep()

    def _init_full_update(self):
        self._command(0x82,b'\x08')
        self._command(0X50,b'\x97')

        self._command(0x20)
        self._data(self.LUT_20_VCOMDC)
        self._command(0x21)
        self._data(self.LUT_21_WW)
        self._command(0x22)
        self._data(self.LUT_22_BW)
        self._command(0x23)
        self._data(self.LUT_23_WB)
        self._command(0x24)
        self._data(self.LUT_24_BB)

    def _wake_up(self):
        self.reset()
        self._command(0x01,b'\x03\x00\x2B\x2B\x03')
        self._command(0x06,b'\x17\x17\x17')
        self._command(0x04);
        self.wait_until_idle()

        self._command(0x00,b'\xBF\x0D')
        self._command(0x30,b'\x3A')

        self._command(0x61)
        self._data(bytearray([EPD_WIDTH]))
        self._data(bytearray([EPD_HEIGHT >> 8]))
        self._data(bytearray([EPD_HEIGHT & 0xFF]))
        self._init_full_update()

    def _sleep(self):
        self._command(0x02)
        self._command(0x07, b'\xA5')
        self.wait_until_idle()
