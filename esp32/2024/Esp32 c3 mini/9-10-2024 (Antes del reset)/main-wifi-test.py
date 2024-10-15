import network
import time

# Desactivar el WiFi antes de activarlo de nuevo
def restart_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(False)
    time.sleep(2)  # Esperar un par de segundos antes de volver a activarlo
    wlan.active(True)

# Datos de la red WiFi
ssid = 'Telecentro-e198'
password = 'UMM5GDZWUDZX'

# Federico's Galaxy S22 Ultra;11111111

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    # Verificar si ya está conectado
    if not wlan.isconnected():
        print('Conectando a la red WiFi...')
        wlan.connect(ssid, password)
        
        # Esperar a que se conecte
        while not wlan.isconnected():
            print('.', end='')
            time.sleep(1)
    
    print('Conexión exitosa!')
    print('Datos de la red:', wlan.ifconfig())

# Reiniciar el WiFi y conectar
restart_wifi()
connect_wifi()

