from machine import Pin

# PIN output
LED_STATUS = Pin(8, Pin.OUT)
LED_WEB_SERVER = Pin(10, Pin.OUT)  # GREEN
LED_MQTT = Pin(7, Pin.OUT)  # RED
LED_WIFI = Pin(20, Pin.OUT)  # BLUE

NETWORK_PROFILES = 'data/wifi.networks'
DATA_CORE_PATH = 'data/core_data.json'

# Configuración del pin del botón de reset
RESET_PIN = Pin(9, Pin.IN, Pin.PULL_UP)

def off_led_core():
    LED_WEB_SERVER.off()
    LED_MQTT.off()
    LED_WIFI.off()
