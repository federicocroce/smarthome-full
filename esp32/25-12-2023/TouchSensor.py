from machine import Pin
import time
from time import sleep
from Delay import delay_seconds


class Touch:
    def __init__(self, pin):
        self.touch_pin = Pin(pin, Pin.IN)
        self.value = False
        self.flag_touch = False

        
    def is_touching(self, callback, time_threshold = 0.5):
        touch_pin = self.touch_pin
        value = False
        try: #Try getting Touch state
            if touch_pin.value() == 1:
                value = True
        except: #If error, return True
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
    
# touch = Touch(pin=4)




# while True:
#     print('touch', touch.set_touch())
#     touch.get_value()
#     sleep(0.5)




# from machine import Pin, TouchPad
# from time import sleep

# def limit_value(value, minimum, maximum):
#     return max(minimum, min(value, maximum))

# class Touch:
#     def __init__(self, pin):
#         self.touch = TouchPad(Pin(pin))
#         self.value = 0
    
#     def set_touch(self):
#         touch = self.touch
#         touch_value = limit_value(touch.read(), 10, 1000)
#         print('touch', touch_value)
#         # value = touch.read()
#         # self.value = value
#         # return value
            
#     def get_value(self):
#         return self.value
    
# # touch = Touch(pin=4)




# while True:
#     print('touch', touch.set_touch())
#     touch.get_value()
#     sleep(0.5)
