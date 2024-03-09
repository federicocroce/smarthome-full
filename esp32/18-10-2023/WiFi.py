import machine
import network
import utime as time
import urequests
import _thread


wifi = None
is_connected = False

def wifi_init(ssid,password, led=None):
    global is_connected
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
        time.sleep(1)
        internet_thread = _thread.start_new_thread(check_internet_connection, ())

        if(led):
            led.on()
    
    def handle_wifi_connection():
        while not is_wifi_connected():
            led.on()
            time.sleep(0.1)
            led.off()
            time.sleep(0.1)
            pass
            
    def handle_wifi_disconnect():
        print("¡Se ha perdido la conexión WiFi!")
        if(led):
            led.off()
        handle_wifi_connection()
        print("¡Conexión WiFi restablecida!")
        

        if(led):
            led.on()

        return


    
    def check_internet_connection():
        global is_connected
        print("ENTRA AL HILO", is_connected)
        
        while True:
            if network.WLAN(network.STA_IF).isconnected():
                time.sleep(1)
                try:
                    print("ENTRA AL TRY", is_connected)
                    # Intenta hacer una solicitud a una dirección IP local (ejemplo: la dirección IP de tu router)
                    response = urequests.get('https://www.google.com')
                    response.close()
                    print("TIENE")
                    is_connected = True  # La solicitud tuvo éxito, por lo que hay conectividad a la red local.
                    
                except Exception as e:
                    print("NO")
                    is_connected = False  # La solicitud falló, lo que podría indicar la falta de acceso a Internet.
                except KeyboardInterrupt:
                    print("\nBucle interrumpido por el usuario.")
            

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