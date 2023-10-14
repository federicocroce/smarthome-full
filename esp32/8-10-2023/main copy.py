from machine import Pin, SoftI2C
from time import sleep, localtime
import time as MOD_TIME

from TemperatureHumidity import TemperatureHumidity
from Touch import Touch
from DimmerPWM import DimmerPWM
from Delay import delay_init
from Display import Display, getWidth

# Seteo de delays
th_delay = delay_init()
increase_decrease_delay = delay_init()

# seteo de touch
touch_increase = Touch(4)
touch_decrease = Touch(15)

dimmer = DimmerPWM(2, 100)

display = Display(scl=22, sda=21)

th_sensor = TemperatureHumidity(23)


def set_temperature_humidity_display(temperature, humidity):
    temperature_str = f'Temp: {temperature}c a'
    humidity_str = f'Humedad: {humidity}%'
    # print(localtime())
    year, month, day, hour, minutes, sec, b, c = localtime()  # type: ignore
    display.fill(0)
    display.text(f'{day}/{month}/{str(year)[2:4]}', 0, 0, 1)
    display.text(f'{hour}:{minutes}:{sec}', 65, 0, 1)
    display.hline(0, 12, getWidth(), 1)
    display.text(temperature_str, 0, 30, 1)
    display.text(humidity_str, 0, 40, 1)
    display.show()


def increase_decrease_touch():
    duty = dimmer.get_duty()
    if (touch_increase.set_touch() < 300 and duty > 0):
        duty -= 2
    elif (touch_decrease.set_touch() < 300 and duty < 100):
        duty += 2
    # print('duty', duty)
    dimmer.set_dimmer(duty)


def get_th_and_render():
    th = th_sensor.get_temperature_humidity()
    set_temperature_humidity_display(
        temperature=th['temperature'], humidity=th['humidity'])


while True:
    # Controla la intensidad del LED
    increase_decrease_delay(increase_decrease_touch, 30)
    # Controla y renderiza en el display la temperatura y la humedad
    th_delay(get_th_and_render, 1000)
