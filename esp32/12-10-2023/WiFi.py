import machine
import network
import utime as time


wifi = None

def wifi_init(ssid,password, led=None):

    def connect_to_wifi():
        sta_if = network.WLAN(network.STA_IF)
        sta_if.active(True)
        if not sta_if.isconnected():
            print("Conectando al WiFi...")
            sta_if.connect(ssid, password)
            while not sta_if.isconnected():
                led.on()
                time.sleep(0.1)
                led.off()
                time.sleep(0.1)
                pass
        print("Conexión WiFi establecida. Dirección IP:", sta_if.ifconfig()[0])
        if(led):
            led.on()
            
            
    def handle_wifi_disconnect():
        print("¡Se ha perdido la conexión WiFi!")
        if(led):
            led.off()
        while not network.WLAN(network.STA_IF).isconnected():
            led.on()
            time.sleep(0.1)
            led.off()
            time.sleep(0.1)
            pass
        print("¡Conexión WiFi restablecida!")
        

        if(led):
            led.on()

        return

    def is_wifi_connected():
        return network.WLAN(network.STA_IF).isconnected()

    connect_to_wifi()
    return (handle_wifi_disconnect, is_wifi_connected)


def get_wifi():
    return wifi

def set_wifi(ssid, password, led=None):
    global wifi  # Usamos la variable global
    if wifi is None:
        # Creamos la instancia del store si aún no existe
        wifi = wifi_init(ssid, password, led)
    return wifi