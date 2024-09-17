from machine import Pin, SoftI2C
import sh1106


DISPLAY_WIDTH = 128
DISPLAY_HEIGHT = 64
FREQ=400000

def Display(scl, sda, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, freq=FREQ):
    i2c = SoftI2C(scl=Pin(scl), sda=Pin(sda), freq=freq)
    display = sh1106.SH1106_I2C(width, height, i2c, Pin(16), 0x3c)
    display.sleep(False)
    display.fill(0)
    display.show()
    return display
def getWidth():
    return DISPLAY_WIDTH
def getHeight():
    return DISPLAY_HEIGHT



# Implementacion

# display = Display(scl=22, sda=21)
# 
# display.hline(0,10,getWitdh(),1)
# display.show()