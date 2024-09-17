from machine import Pin, TouchPad
import time
from time import sleep
from Delay import delay_seconds

# touch_pin = TouchPad(Pin(4))
# 
# 
# def set_touch():
#     value = touch_pin.read()
#     return ({'value': value})
# 
# while True:
#     value = set_touch()
#     print('value', value)
#     sleep(0.5)

def limit_value(value, minimum, maximum):
    return max(minimum, min(value, maximum))

class Touch:
    def __init__(self, pin):
        self.touch_pin = TouchPad(Pin(pin))
        self.value = False
        self.callback_timer = False
        self.flag_touch = False
        self.touch_pin.config(500)
        
    def is_touching(self, callback, time_threshold = 0.5):
        touch_pin = self.touch_pin
        value = False
        try: #Try getting Touch state
#             print(touch_pin.read())
            if touch_pin.read() < 200:
#                 print(touch_pin.read())
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
#                 callback()
                delay_seconds(callback, time_threshold)

            
            
#         if callback is not None:
#             print("1", self.callback_timer)
#             if value == True:
#                 if self.callback_timer is not None:
#                     print("True")
#                     # Cancelar el temporizador si touch se volvió True antes de que se ejecutara el callback
#                     self.callback_timer = None
#             else:
#                 # Iniciar el temporizador cuando touch se vuelve False por primera vez
#                 if self.callback_timer is None:
#                     print("False")
#                     self.callback_timer = time.time()
#             
#             if not value and self.callback_timer is not None and (time.time() - self.callback_timer) >= time_threshold:
#                 callback()
#                 callback_timer = None  # Reiniciar el temporizador después de llamar al callback
#             sleep(0.5)
            
        self.value = value
        return value
            
    def get_value(self):
        return self.value
    
    
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