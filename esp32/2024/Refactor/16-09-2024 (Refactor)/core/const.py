import machine

NETWORK_PROFILES = 'data/wifi.networks'

# Configuración del pin del botón de reset
RESET_PIN = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP)
