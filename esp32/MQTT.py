import machine
import time
from umqtt.robust import MQTTClient
import ujson

def connect_mqtt(client_id, mqtt_server, mqtt_user, mqtt_password,LED_MQTT=None):

    def connect_mqtt():
        ssl_params = dict()
        # ssl_params["cadata"] = CERTIFICATE
        ssl_params["server_hostname"] = mqtt_server
        
        client = MQTTClient(client_id, mqtt_server, user=mqtt_user,
                            password=mqtt_password, ssl=True, ssl_params=ssl_params)
    
        client.connect()
        print("MQTT connection established")
        if(LED_MQTT):
            LED_MQTT.on()
        return client
    
    client = connect_mqtt()
        
    # def check_mqtt_connection():
    #     try:
    #         client.ping()
    #         print("Conexión MQTT activa")
    #         client.check_msg()
    #         return True
    #     except OSError as e:
    #         print("Error en la conexión MQTT:", e)
    #         print('LEDMQTT', LED_MQTT)
    #         if(LED_MQTT):
    #             LED_MQTT.off()
    #         return False
    last_ping = time.time()
    def check_mqtt_connection(ping_interval = 60):
        nonlocal last_ping
        # nonlocal ping_interval
        nonlocal client
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
            machine.reset()
            return False
    
    def reconnect_mqtt():
        if not client.ping():
            client.disconnect()
            print("Desconectado del broker MQTT")
            time.sleep(5)  # Esperar antes de intentar reconectar
            new_client = connect_mqtt()
            return new_client
        return client
    
    def update_device(device, value):
        client.publish('update_device', ujson.dumps({"device": device, "value": value}))
    

    return (client, check_mqtt_connection, reconnect_mqtt, update_device)