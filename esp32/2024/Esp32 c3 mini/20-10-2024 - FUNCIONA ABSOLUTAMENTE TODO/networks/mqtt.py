import machine
import time
import umqtt.robust
from umqtt.robust import MQTTClient
import ujson
import ssl
import _thread
from utilities.queue import Queue

mqtt_queue = Queue()

# global
mqtt_topics = None
LED_MQTT = None

last_ping = time.time()
mqtt_client = None
client = None
mqtt_is_connected = 0
MQTT_SSL = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
MQTT_SSL.verify_mode = ssl.CERT_NONE

def mqtt_init(client_id, mqtt_server, mqtt_user, mqtt_password, topics, callback, led=None):
    global client, mqtt_topics

    mqtt_topics = topics
    LED_MQTT = led

    ssl_params = dict()
    ssl_params["server_hostname"] = mqtt_server
    print("ssl_params", ssl_params)
    print("connect_mqtt client")
    client = MQTTClient(client_id, mqtt_server, user=mqtt_user,
                        password=mqtt_password, keepalive=60, ssl=MQTT_SSL)

    print("connect_mqtt connect", client)
    client.connect()
    print("luego connect_mqtt connect")

    client.set_callback(callback)

    print("MQTT connection established")
    if (LED_MQTT):
        LED_MQTT.on()

    print("client.ping()", client.ping())


def check_mqtt_connection(ping_interval=1):
    global last_ping
    global client
    current_ping_internal = 60
    if mqtt_is_connected < 2:
        current_ping_internal = 1

    try:
        if (time.time() - last_ping) >= current_ping_internal:
            client.ping()
            last_ping = time.time()
            now = time.localtime()
            print(
                f"Pinging MQTT Broker, last ping :: {now[0]}/{now[1]}/{now[2]} {now[3]}:{now[4]}:{now[5]}")
    except OSError as e:
        print("Error en la conexión MQTT:", e)
        if (LED_MQTT):
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
        if (LED_MQTT):
            LED_MQTT.on()
        if callback:
            callback()
        print("conexion mqtt establecida")
    mqtt_is_connected = mqtt_is_connected + 1


def pause_mqtt():
    global mqtt_is_connected

    if (LED_MQTT):
        LED_MQTT.off()
    mqtt_is_connected = 0


def queue_put(device, value):
    try:
        item_queue = {'topic': 'update_device', 'msg': ujson.dumps({"device": device, "value": value})}
        mqtt_queue.put(item_queue)
    except Exception as e:
        print("Error al agregar a la cola:", e)
        
        
        
# Función para procesar la cola de mensajes MQTT
def mqtt_publish_worker():
    global client
    while True:
        if not mqtt_queue.empty():
            item = mqtt_queue.get()
            try:
                if client is not None:
                    topic = item.get("topic")
                    msg = item.get("msg")
                    print("PUBLICA EN EL SERVER", topic, msg)
                    client.publish(topic, msg)
            except Exception as e:
                print("Error en la publicación MQTT:", e)

# Inicia un hilo para manejar la publicación de mensajes
_thread.start_new_thread(mqtt_publish_worker, ())

