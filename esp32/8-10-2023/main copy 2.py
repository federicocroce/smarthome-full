

import network
from umqtt.simple import MQTTClient
import ssl
import ujson
from machine import Pin
from DimmerPWM import DimmerPWM
import utime as time
from UtilitiesRGB import spectrumrgb_to_rgb_limit_100, configurar_temperatura_color


RED = DimmerPWM(pin=5, default=100)
GREEN = DimmerPWM(pin=18, default=100)
BLUE = DimmerPWM(pin=19, default=100)

LED_STATUS = Pin(2, Pin.OUT)
LED_MQTT = Pin(27, Pin.OUT) #RED
LED_WIFI = Pin(26, Pin.OUT) #BLUE


LED_WIFI.off()
LED_MQTT.off()

# Configurar la conexión Wi-Fi
# WiFi Setup
WIFI_SSID = "WiFi-Arnet-knt5_2,4"
WIFI_PASSWORD = "cmq3ntce"
# WIFI_SSID = "Federico's Galaxy S22 Ultra"
# WIFI_PASSWORD = "11111111"

# Configurar los detalles del broker MQTT
mqtt_server = "afdc512217a942639f02c4cf4cce5fd0.s1.eu.hivemq.cloud"
mqtt_port = 8883  # Puerto predeterminado para MQTT
mqtt_user = "fcroce"
mqtt_password = "34023936Fc"

# Nombre de cliente MQTT
client_id = "esp32_client"

def conectar_mqtt():
    mqtt_client = MQTTClient(client_id, mqtt_server, user=mqtt_user,
                         password=mqtt_password, ssl=True, ssl_params=ssl_params)
    # Conectarse al broker MQTT
    mqtt_client.connect()
    LED_MQTT.on()
    print("Conexión MQTT establecida")
    return mqtt_client

def verificar_conexion_mqtt(client, COUNT):
    try:
        client.ping()
        print("Conexión MQTT activa", COUNT)
        return True
    except OSError as e:
        print("Error en la conexión MQTT:", e)
        LED_MQTT.off()
        return False
    
def reconectar_mqtt(client):
    client.disconnect()
    print("Desconectado del broker MQTT")
    time.sleep(5)  # Esperar antes de intentar reconectar
    client = conectar_mqtt()
    return client


# Callback que se llama cuando se recibe un mensaje MQTT
def callback(topic, msg):
    print("Mensaje recibido: Topic = {}, Mensaje = {}".format(topic, msg))
    try:
        # Intentar decodificar el JSON
        data = ujson.loads(msg)
        print('DATA:', data)
        # Extraer el valor del LED1 si el JSON es válido
        led1_data = data.get('led1', {})
        brightness = led1_data.get('brightness') 
        spectrumrgb = led1_data.get('color', {}).get('spectrumRGB')
        color_name = led1_data.get('color', {}).get('name')
        temperature = led1_data.get('color', {}).get('temperature')
        is_on = led1_data.get('on')

        print('Brightness:', brightness)
        print('Color:', spectrumrgb)
        print('Is On:', is_on)
        # led1.set_dimmer(brightness, is_on)
        # r, g, b = spectrumrgb_to_rgb_limit_100(10026796, brightness)
        # if(spectrumrgb):
        # r, g, b = spectrumrgb_to_rgb(spectrumrgb)
        # print('red1, green2, blue3', r, g, b)
        red, green, blue = 0, 0, 0
        if color_name == 'blanco':
           spectrumrgb = 16777215
        if not spectrumrgb and temperature:
            red, green, blue = configurar_temperatura_color(temperature)
        else:
            red, green, blue = spectrumrgb_to_rgb_limit_100(
            spectrumrgb, brightness)
        print('red, green, blue', red, green, blue)
        RED.set_dimmer(red, is_on)
        GREEN.set_dimmer(green, is_on)
        BLUE.set_dimmer(blue, is_on)
    except ValueError:
        # Si no es un JSON válido, imprimir el mensaje como texto simple
        print('Mensaje recibido:', msg.decode('utf-8'))


# Connect to WiFi
wifi_client = network.WLAN(network.STA_IF)
wifi_client.active(True)
print("Connecting device to WiFi")
wifi_client.connect(WIFI_SSID, WIFI_PASSWORD)

# Wait until WiFi is Connected
while not wifi_client.isconnected():
    print("Connecting")
    time.sleep(0.1)

print("WiFi Connected!")
print(wifi_client.ifconfig())

def connect_to_wifi():
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    if not sta_if.isconnected():
        print("Conectando al WiFi...")
        sta_if.connect(wifi_ssid, wifi_password)
        while not sta_if.isconnected():
            pass
    print("Conexión WiFi establecida. Dirección IP:", sta_if.ifconfig()[0])
    LED_WIFI.on()


def handle_wifi_disconnect():
    LED_STATUS.off()  # Apaga el LED cuando se desconecta
    print("¡Se ha perdido la conexión WiFi!")
    LED_WIFI.off()
    while not network.WLAN(network.STA_IF).isconnected():
        pass
    print("¡Conexión WiFi restablecida!")
    LED_WIFI.on()


connect_to_wifi()

# ssl_params["cert_reqs"] = ssl.CERT_REQUIRED
ssl_params = dict()
# ssl_params["cadata"] = CERTIFICATE
ssl_params["server_hostname"] = mqtt_server
# Conectar al broker MQTT
mqtt_client = conectar_mqtt()

# Establecer la función de callback
mqtt_client.set_callback(callback)


# Suscribirse a un topic
mqtt_topic = "mi_topic"
mqtt_client.subscribe(mqtt_topic)

# Publicar un mensaje
mqtt_client.publish(mqtt_topic, "Hola desde ESP32")
COUNT = 0
# Esperar a recibir mensajes
conectado = True
LED_MQTT.on()

# while True:
#     try:
#         # LED_STATUS.on()
#         # time.sleep(2)
#         # LED_STATUS.off()
#         # time.sleep(2)
        
#         mqtt_client.wait_msg()
#         time.sleep(0.01)  # Pequeño retraso entre iteraciones

#         # Additional logic or tasks can be performed here
#         # time.sleep(0.1)  # Small delay between iterations
#     except KeyboardInterrupt:
#         break


# mqtt_client.disconnect()

# mqtt_client.wait_msg()   
    
start_time = time.time()    
while True:
    print('Entra 1')
    try:
        COUNT = COUNT + 1
        print('Entra 2')
        mqtt_client.check_msg()
        print('Esta conectado', COUNT)
        time.sleep(1)
        # time.sleep(0.01) 
        # current_time = time.time()
        # if not network.WLAN(network.STA_IF).isconnected():
        #     print('Entra al IF')
        #     handle_wifi_disconnect()
        # else:
        #     print('Entra ELSE')
        #     # mqtt_client.check_msg()
        #     # time.sleep(0.1)
        # #     # LED_STATUS.on()  # Enciende el LED cuando está conectado
        # #     # Aquí puedes agregar cualquier otra lógica o tareas que desees realizar
        # #     print('Esta conectado', COUNT, network.WLAN(network.STA_IF).isconnected())
        #     # COUNT = COUNT + 1
        # #     # time.sleep(1)  # Pausa de 1 segundo
        #     # if not verificar_conexion_mqtt(mqtt_client, COUNT):
        #     #     mqtt_client = reconectar_mqtt(mqtt_client)
        #     #     if mqtt_client is None:  # Si no se puede reconectar, detener el bucle
        #     #         conectado = False
        #     # else:   
        #     mqtt_client.wait_msg()
        #     print('Esta conectado', COUNT)
        #     time.sleep(0.01) 
        
        # if current_time - start_time >= 5:
        #     time.sleep(1)  # Pequeño retraso antes de desconectar
        #     mqtt_client.disconnect()
        #     break

        # mqtt_client.check_msg()
        # time.sleep(0.1)  # Pequeño retraso entre iteraciones
    except OSError as e:
        print("Error en la ejecucion", e)
        break



    # time.sleep(10)
    # #Desconectarse del broker MQTT
    # mqtt_client.disconnect()
