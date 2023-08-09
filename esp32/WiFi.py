import machine
import network
import utime as time


def wifi_init(ssid,password, led=None):
    # Connect to WiFi
    # wifi_client = network.WLAN(network.STA_IF)
    # wifi_client.active(True)
    # print("Connecting device to WiFi")
    # wifi_client.connect(ssid, password)

    # # Wait until WiFi is Connected
    # while not wifi_client.isconnected():
    #     print("Connecting")
    #     time.sleep(0.1)

    # print("WiFi Connected!")
    # print(wifi_client.ifconfig())

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
        machine.reset()
        return

    def is_wifi_connected():
        return network.WLAN(network.STA_IF).isconnected()

    connect_to_wifi()
    return (handle_wifi_disconnect, is_wifi_connected)