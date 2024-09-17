from machine import Pin
import time
from time import sleep
from Delay import delay_seconds


class Touch:
    def __init__(self, pin):
        self.touch_pin = Pin(pin, Pin.IN)
        self.value = False
        self.touch_type = 'pulse'
        self.flag_touch = False
        self.touching_time = 0

        
    def is_touching(self, callback_touch_end_touch, callback_pulse, callback_dimmer, time_threshold = 0.5):
        touch_pin = self.touch_pin
        value = False
        try: #Try getting Touch state
            if touch_pin.value() == 1:
#                 print("self.touching_time", self.touching_time)
                self.touching_time = self.touching_time + 0.02

                if self.touching_time > 1:
#                     print("self.touching_time > 1", self.touching_time)

                    self.touch_type = 'dimmer'
                    if callback_dimmer is not None:
#                         print("Ejecuta callback_dimmer")
                        callback_dimmer()
#                     print("Touching")
                value = True
                
        except: #If error, return True
            value = True
            return True
        
   
        if value == True and self.flag_touch == False:
            self.flag_touch = True

        elif value == False and self.flag_touch == True:
            print("Not Touching")
            self.flag_touch = False
            self.touching_time = 0
#             print("self.touch_type", self.touch_type)
            if callback_pulse is not None and self.touch_type == 'pulse':
                callback_pulse()
            if callback_touch_end_touch is not None:
                delay_seconds(callback_touch_end_touch, time_threshold)
            self.touch_type = 'pulse'


            
        self.value = value
        return value
#         return {"status": value, "touch_type": self.touch_type}
    
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
