import machine
import time
from umqtt.robust import MQTTClient
import ujson

mqtt_client = None
client = None
mqtt_is_connected = 0

def mqtt_init(client_id, mqtt_server, mqtt_user, mqtt_password,mqtt_topic, callback, LED_MQTT=None):
    global client

    def connect_mqtt():
        global client

        ssl_params = dict()
        ssl_params["server_hostname"] = mqtt_server
        print("connect_mqtt client")
        client = MQTTClient(client_id, mqtt_server, user=mqtt_user, password=mqtt_password, keepalive=60, ssl=True, ssl_params=ssl_params)
        print("connect_mqtt connect")
        client.connect()
        print("luego connect_mqtt connect")

        client.set_callback(callback)
        
        print("MQTT connection established")
        if(LED_MQTT):
            LED_MQTT.on()
        
        print("client.ping()",client.ping())
    

    connect_mqtt()
        
    last_ping = time.time()
    
    def keep_mqtt_connection():
        global client
        global mqtt_is_connected
        
        client.check_msg()
        
        if mqtt_is_connected == 1:
            client.subscribe(mqtt_topic)
            if(LED_MQTT):
                LED_MQTT.on()
            print("conexion mqtt establecida")
        mqtt_is_connected = mqtt_is_connected + 1
        
    def pause_mqtt():
        global mqtt_is_connected
        
        if(LED_MQTT):
            LED_MQTT.off()
        mqtt_is_connected = 0
    
    def update_device(device, value):
        global client
        
        if client is not None:
            client.publish('update_device', ujson.dumps({"device": device, "value": value}))
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


def set_mqtt(client_id, mqtt_server, mqtt_user, mqtt_password,mqtt_topic, callback, LED_MQTT=None):
    global mqtt_client  # Usamos la variable global
    
    if mqtt_client is None:
        # Creamos la instancia del store si aún no existe
        mqtt_client = mqtt_init(client_id, mqtt_server, mqtt_user, mqtt_password, mqtt_topic, callback, LED_MQTT)
    return mqtt_client