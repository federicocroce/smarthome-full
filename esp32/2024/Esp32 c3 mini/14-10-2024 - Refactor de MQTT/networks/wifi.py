import network
import time
import socket
from machine import RTC
from utilities.common import blinking_led

# Variables globales
wlan = network.WLAN(network.STA_IF)
ssid = None
password = None
led_wifi = None
rtc = RTC()
is_connected = False


def init_wifi(ssid_param, password_param, led_wifi_param):
    global ssid, password, led_wifi
    ssid = ssid_param
    password = password_param
    led_wifi = led_wifi_param
    
    if wlan.isconnected():
        wlan.disconnect()

    


def connect():
    global is_connected
    wlan.active(False)
    time.sleep(1)
    wlan.active(True)
    if not wlan.isconnected():
        print(f"Conectando a la red {ssid}...")
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            blinking_led(led_wifi, 0.2)
    print("Conexión establecida:", wlan.ifconfig())
    is_connected = True
    if led_wifi:
        led_wifi.on()


def check_internet():
    try:
        addr_info = socket.getaddrinfo('google.com', 80)
        addr = addr_info[0][-1]
        s = socket.socket()
        s.settimeout(3)
        s.connect(addr)
        s.close()
        return True
    except Exception as e:
        print("No se puede alcanzar Google:", e)
        return False


def check_connection():
    global is_connected
    if wlan.isconnected():
        if check_internet():
            print("Acceso a Internet")
            if led_wifi:
                led_wifi.on()
            is_connected = True
            return True
        else:
            print("Sin acceso a Internet")
            is_connected = False
            return False
    else:
        print("Desconectado del WiFi. Intentando reconectar...")
        connect()


def get_time():
    return "{}-{}-{} {}:{}:{}".format(*rtc.datetime()[:6])
