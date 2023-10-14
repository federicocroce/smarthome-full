import machine
import time
from umqtt.simple import MQTTClient
import ujson

mqtt_client = None

def mqtt_init(client_id, mqtt_server, mqtt_user, mqtt_password,mqtt_topic, callback, LED_MQTT=None):
    
    client = None

    def connect_mqtt():
        nonlocal client
        client = None
        print("connect_mqtt")
        ssl_params = dict()
        # ssl_params["cadata"] = CERTIFICATE
        ssl_params["server_hostname"] = mqtt_server
        print("connect_mqtt client")
        client = MQTTClient(client_id, mqtt_server, user=mqtt_user,
                            password=mqtt_password, ssl=True, ssl_params=ssl_params)
        print("connect_mqtt connect")
        client.connect(clean_session=True)
        print("luego connect_mqtt connect")

        client.set_callback(callback)
        # Suscribirse a un topic
        client.subscribe(mqtt_topic)

        print("MQTT connection established")
        if(LED_MQTT):
            LED_MQTT.on()
    

    connect_mqtt()
        
    last_ping = time.time()
    
    def check_mqtt_connection(ping_interval = 60):
        nonlocal last_ping
        nonlocal client
        # nonlocal ping_interval
        # print("time.time()", time.time())
        # print("last_ping", last_ping)
        try:
            if (time.time() - last_ping) >= ping_interval:
                client.ping()
                last_ping = time.time()
                now = time.localtime()
                print(f"Pinging MQTT Broker, last ping :: {now[0]}/{now[1]}/{now[2]} {now[3]}:{now[4]}:{now[5]}")
        except OSError as e:
            print("Error en la conexión MQTT:", e)
            print('LEDMQTT', LED_MQTT)
            if(LED_MQTT):
                LED_MQTT.off()
#             machine.reset()
            return False
    
    def reconnect_mqtt():
        connect_mqtt()
#         nonlocal client
#         client.set_callback(callback)
#         # Suscribirse a un topic
#         client.subscribe(mqtt_topic)
        
# #         if not client.ping():
#         print("reconnect_mqtt ", client)
#         print("reconnect_mqtt client.ping()", client.ping)
#         client.disconnect()
# #         print("Desconectado del broker MQTT")
#         time.sleep(5)  # Esperar antes de intentar reconectar
#         print("reconnect_mqtt luego de 5")
# # #             client = connect_mqtt()
#         client = connect_mqtt()
#         mqtt_client = {"mqtt_client": client, "check_mqtt_connection": check_mqtt_connection, "reconnect_mqtt": reconnect_mqtt, "update_device": update_device}
            
    
    def update_device(device, value):
        nonlocal client
        client.publish('update_device', ujson.dumps({"device": device, "value": value}))
    

    return {"mqtt_client": client, "check_mqtt_connection": check_mqtt_connection, "reconnect_mqtt": reconnect_mqtt, "update_device": update_device, "led_mqtt": LED_MQTT}

def get_mqtt():
    return mqtt_client


def set_mqtt(client_id, mqtt_server, mqtt_user, mqtt_password,mqtt_topic, callback, LED_MQTT=None):
    global mqtt_client  # Usamos la variable global
    if mqtt_client is None:
        # Creamos la instancia del store si aún no existe
        mqtt_client = mqtt_init(client_id, mqtt_server, mqtt_user, mqtt_password, mqtt_topic, callback, LED_MQTT)
        print("mqtt_client", mqtt_client)
    return mqtt_client