from machine import Pin, TouchPad
import time
from time import sleep
from utilities.Delay import delay_seconds


def limit_value(value, minimum, maximum):
    return max(minimum, min(value, maximum))


class Touch:
    def __init__(self, pin):
        self.touch_pin = TouchPad(Pin(pin))
        self.value = False
        self.callback_timer = False
        self.flag_touch = False
        self.touch_pin.config(500)

    def is_touching(self, callback, time_threshold=0.5):
        touch_pin = self.touch_pin
        value = False
        try:  # Try getting Touch state
            #             print(touch_pin.read())
            if touch_pin.read() < 200:
                #                 print(touch_pin.read())
                value = True
        except:  # If error, return True
            value = True
            return True

        if callback is not None:
            if value == True and self.flag_touch == False:
                self.flag_touch = True
                print("Touching")
            elif value == False and self.flag_touch == True:
                print("Not Touching")
                self.flag_touch = False
                delay_seconds(callback, time_threshold)

        self.value = value
        return value

    def get_value(self):
        return self.value
