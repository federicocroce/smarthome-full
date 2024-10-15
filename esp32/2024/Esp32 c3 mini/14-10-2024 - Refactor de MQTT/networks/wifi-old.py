
import network
import time
from machine import RTC
import socket

# Configuración del WiFi
SSID = 'WiFi-Arnet-knt5_2,4_EXT'
PASSWORD = 'cmq3ntce'


# SSID = "Federico's Galaxy S22 Ultra"
# PASSWORD = '11111111'

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(False)
    time.sleep(1)
    wlan.active(True)
    print("wlan.isconnected() SIN ANTENA", wlan.isconnected())
    if not wlan.isconnected():
        print(f"Conectando a la red {SSID}...")
        wlan.connect(SSID, PASSWORD)
        while not wlan.isconnected():
            time.sleep(1)
    print("Conexión establecida:", wlan.ifconfig())
    return wlan

def check_internet():
    try:
        # Realiza un ping a Google para verificar la conexión a Internet
        addr_info = socket.getaddrinfo('google.com', 80)
        addr = addr_info[0][-1]
        print("addr", addr)
        s = socket.socket()
        s.settimeout(3)
        s.connect(addr)
        s.close()
        return True
    except Exception as e:
        print("No se puede alcanzar Google:", e)
        return False

def check_wifi(wlan):
    if wlan.isconnected():
        internet_status = "Acceso a Internet" if check_internet() else "Sin acceso a Internet"
        print(f"Conectado al WiFi - {internet_status} - Hora actual: {get_time()}")
    else:
        print("Desconectado del WiFi. Intentando reconectar...")
        connect_wifi()

def get_time():
    rtc = RTC()
    return "{}-{}-{} {}:{}:{}".format(*rtc.datetime()[:6])

def main():
    wlan = connect_wifi()
    print("wlan", wlan)
    while True:
        check_wifi(wlan)
        time.sleep(5)

if __name__ == "__main__":
    main()


