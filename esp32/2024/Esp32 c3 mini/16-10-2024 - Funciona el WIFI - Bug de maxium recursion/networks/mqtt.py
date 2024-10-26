import machine
import time
# import umqtt.robust
from umqtt.robust import MQTTClient
import json
import ssl

mqtt_client = None
client = None
mqtt_is_connected = 0
MQTT_SSL = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
MQTT_SSL.verify_mode = ssl.CERT_NONE

# print(umqtt.robust.__file__)

def mqtt_init(client_id, mqtt_server, mqtt_user, mqtt_password, mqtt_topics, callback, LED_MQTT=None):
    global client

    def connect_mqtt():
        global client

        ssl_params = dict()
        ssl_params["server_hostname"] = mqtt_server
        print("ssl_params", ssl_params)
        print("connect_mqtt client")
        client = MQTTClient(client_id, mqtt_server, user=mqtt_user, password=mqtt_password, keepalive=60, ssl=MQTT_SSL)
        
        print("connect_mqtt connect", client)
        client.connect()
        print("luego connect_mqtt connect")

        client.set_callback(callback)
        
        print("MQTT connection established")
        if(LED_MQTT):
            LED_MQTT.on()
        
        print("client.ping()",client.ping())
    

    connect_mqtt()
        
    last_ping = time.time()
    
    
    def check_mqtt_connection(ping_interval = 1):
        nonlocal last_ping
        global client
        current_ping_internal = 60
        # nonlocal ping_interval
        # print("time.time()", time.time())
        # print("last_ping", last_ping)
        if mqtt_is_connected < 2:
            current_ping_internal = 1
        
        try:
            if (time.time() - last_ping) >= current_ping_internal:
                client.ping()
                last_ping = time.time()
                now = time.localtime()
                print(f"Pinging MQTT Broker, last ping :: {now[0]}/{now[1]}/{now[2]} {now[3]}:{now[4]}:{now[5]}")
        except OSError as e:
            print("Error en la conexión MQTT:", e)
            if(LED_MQTT):
                LED_MQTT.off()
#             machine.reset()
            return False
    
    
    def keep_mqtt_connection(callback=None):
        global client
        global mqtt_is_connected
        client.check_msg()
        check_mqtt_connection()
        if mqtt_is_connected == 1:
            for topic in mqtt_topics:
                client.subscribe(topic)
            if(LED_MQTT):
                LED_MQTT.on()
            if callback:
                callback()
            print("conexion mqtt establecida")
        mqtt_is_connected = mqtt_is_connected + 1
        

        
    def pause_mqtt():
        global mqtt_is_connected
        
        if(LED_MQTT):
            LED_MQTT.off()
        mqtt_is_connected = 0
    
    def update_device(device, getValue):
        global client
        data_formatted = None
        
        while True:
            try:
                data_formatted = json.dumps({"device": "device_name", "value": getValue()})
                print("Data formatted successfully:", data_formatted)
                break  # Salir del bucle si se ejecuta sin errores
            except Exception as e:
                print("Error occurred:", e)
                print("Retrying...")
                time.sleep(1)  # Espera un segundo antes de intentar de nuevo
        
#         data_formatted = json.dumps(
#                 {"device": device, "value": value})
        
        if client is not None:
            client.publish('update_device', data_formatted)
        else:
            print("Intento actualizar")

    return {"mqtt_client": client, "keep_mqtt_connection": keep_mqtt_connection, "pause_mqtt": pause_mqtt, "update_device": update_device, "led_mqtt": LED_MQTT}

def get_mqtt():
    global mqtt_client
    return mqtt_client

def get_mqtt_client():
    global client
    return client

def reset_mqtt():
    global mqtt_client
    mqtt_client = None


def set_mqtt(client_id, mqtt_server, mqtt_user, mqtt_password,mqtt_topics, callback, LED_MQTT=None):
    global mqtt_client  # Usamos la variable global
    
    if mqtt_client is None:
        # Creamos la instancia del store si aún no existe
        mqtt_client = mqtt_init(client_id, mqtt_server, mqtt_user, mqtt_password, mqtt_topics, callback, LED_MQTT)
    return mqtt_client
