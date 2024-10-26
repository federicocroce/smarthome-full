import machine
from machine import Pin


# PIN output
LED_STATUS = Pin(8, Pin.OUT)
LED_WEB_SERVER = Pin(10, Pin.OUT)  # GREEN
LED_MQTT = Pin(7, Pin.OUT)  # RED
LED_WIFI = Pin(20, Pin.OUT)  # BLUE

# PIN input
# INFRA = Pin(16, Pin.IN)

# touch_decrease = TouchSensor(15)
# sensor_init('sensor Pir prueba',34, 15)

NETWORK_PROFILES = 'data/wifi.networks'

# Configuración del pin del botón de reset
RESET_PIN = machine.Pin(9, machine.Pin.IN, machine.Pin.PULL_UP)
