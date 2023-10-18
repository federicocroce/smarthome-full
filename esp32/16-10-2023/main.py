
import network
from umqtt.robust import MQTTClient
import ssl
import ujson
import machine
from machine import Pin
from DimmerPWM import DimmerPWM
import utime as time
from UtilitiesRGB import spectrumrgb_to_rgb_limit_100, configurar_temperatura_color
from WiFi import set_wifi
# from Telegram import send_message
from MQTT import set_mqtt, get_mqtt, reset_mqtt, get_mqtt_client
from Delay import delay_seconds
from DeviceConfig import set_device, init_device, device_config, get_value_from_device_config
from Touch import Touch
import _thread

LED_STATUS = Pin(2, Pin.OUT)
LED_MQTT = Pin(27, Pin.OUT)  # RED
LED_WIFI = Pin(26, Pin.OUT)  # BLUE
INFRA = Pin(16, Pin.IN)

touch_increase = Touch(15)
touch_decrease = Touch(4)

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


# Callback que se llama cuando se recibe un mensaje MQTT
def callback(topic, msg):
    print("Mensaje recibido: Topic = {}, Mensaje = {}".format(topic, msg))
    
    try:
        # Intentar decodificar el JSON
        topic_formatted = str(topic, 'utf-8')
        
        print("topic_formatted", topic_formatted)
        
        if topic_formatted == "mi_topic":
            data = ujson.loads(msg)
            set_device(data)
        if topic_formatted == "device_status":
            print("get_value_from_device_config", get_value_from_device_config("led1")["device"])
            data = get_value_from_device_config("led1")["device"]["get_status"]()
            print("get_status", data)
            client = get_mqtt_client()
            client.publish('status', ujson.dumps(data))
            

    except ValueError:
        # Si no es un JSON válido, imprimir el mensaje como texto simple
        print('Mensaje recibido ERROR:', msg.decode('utf-8'))
    except KeyError as e:
        # Si hay un error al intentar acceder a un atributo de led1_data
        print('Error: No se pudo acceder al atributo de LED1 -', e)


(handle_wifi_disconnect, is_wifi_connected) = set_wifi(WIFI_SSID, WIFI_PASSWORD, LED_WIFI)

init_device()

mqtt = set_mqtt(client_id, mqtt_server, mqtt_user, mqtt_password, ["mi_topic", "device_status"], callback, LED_MQTT)

# send_message("Fede")


def dimmer_led():
#     firebase.patch("led1", {"Brightness": {"brightness": 50}}, bg=False, id=1, cb=None)
    print("Setea el brillo")
#     mqtt_client.publish(mqtt_topic, "Hola desde ESP32")
    while True:
        try:
            device_config['led1']['device']['increase_decrease_touch'](touch_increase, touch_decrease)
            time.sleep_ms(20)
        except KeyboardInterrupt:
            print("\nBucle interrumpido por el usuario.")

led_thread = _thread.start_new_thread(dimmer_led, ())


def reset():
    print("Resetting...")
    time.sleep(5)
    machine.reset()
    
    
def main():
    cbk_dimmer = None
    client = get_mqtt_client()
    
#     nonlocal mqtt
    while True:
        try:
            
            if is_wifi_connected():
                mqtt["keep_mqtt_connection"]()
                time.sleep(0.5)
            else:
                print("ELSE")
                mqtt["pause_mqtt"]()
                handle_wifi_disconnect()
        except OSError as e:
            print("OSError", e)
            reset()


if __name__ == "__main__":
    try:
        main()
    except OSError as e:
        print("OSError", e)
        reset()
    except KeyboardInterrupt as e:
        _thread.interrupt(led_thread)
        print("KeyboardInterrupt Fede", e)
        reset()



# import machine
# import time
# 
# # Configura el pin del sensor TCRT5000
# tcrt_pin = machine.Pin(16, machine.Pin.IN)  # Cambia el número de pin según tu configuración
# 
# flag_to_on_off = True
# is_on = False
# 
# # Función para leer el valor del sensor
# def leer_valor_tcrt():
#     return tcrt_pin.value()  # Lee el valor del pin
# 
# while True:
#     valor = leer_valor_tcrt()
# #     print(valor)
#     if valor == 0:
#         print("Nada detectado")
#         flag_to_on_off = True
#     else:
#         if flag_to_on_off == True:
#             print("Objecto detectado")
#             flag_to_on_off = False
#             is_on = not is_on
#     print("is_on", is_on)
#     time.sleep(1)
    
    
    