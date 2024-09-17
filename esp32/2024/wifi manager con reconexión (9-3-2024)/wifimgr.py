import network
import usocket
import ure
import time
import select


ap_ssid = "WifiManager"
ap_password = "11111111"
ap_authmode = 3  # WPA2

NETWORK_PROFILES = 'wifi.dat'

wlan_ap = network.WLAN(network.AP_IF)
wlan_sta = network.WLAN(network.STA_IF)

server_socket = None
wifi = None


def get_connection(led_web_server=None, led_wifi=None):
    global wifi
    """return a working WLAN(STA_IF) instance or None"""
    
    def blinking_led(custom_sleep=0.1):
        led_wifi.on()
        time.sleep(custom_sleep)
        led_wifi.off()
        time.sleep(custom_sleep)
        

    def do_ping():
        try:
            # Intenta conectarte a www.google.com
            addr = usocket.getaddrinfo("www.google.com", 80)[0][-1]
            s = usocket.socket()
            s.connect(addr)
            s.close()
            return True
        except OSError:
            return False

#     def do_ping(ip_address):
#         icmp_socket = usocket.socket(usocket.AF_INET, usocket.SOCK_RAW, 1)
#         packet = bytearray(64)
#         packet[0] = 0x08  # Tipo de mensaje ICMP (8 para echo request)
#         packet[1] = 0x00  # Código (siempre 0 para echo request)
#         packet[2:4] = b'\x00\x00'  # Checksum inicial (bytes en lugar de entero)
#         packet[4:6] = (1234).to_bytes(2, 'big')  # ID aleatorio
#         packet[6:8] = (1).to_bytes(2, 'big')  # Número de secuencia
#         # Llenar el paquete con datos
#         for i in range(8, len(packet)):
#             packet[i] = i & 0xff
#         # Calcular el checksum
#         checksum = 0
#         for i in range(0, len(packet), 2):
#             checksum += packet[i] * 256 + packet[i+1]
#         checksum = (checksum & 0xffff) + (checksum >> 16)
#         checksum = (~checksum) & 0xffff
#         packet[2:4] = checksum.to_bytes(2, 'big')
#         # Enviar el paquete ICMP
#         icmp_socket.sendto(packet, (ip_address, 1))
#         start_time = time.ticks_ms()
#         # Esperar la respuesta
#         while True:
#             ready = select.select([icmp_socket], [], [], 1)
#             if ready[0]:
#                 response, addr = icmp_socket.recvfrom(1024)
#                 elapsed_time = time.ticks_ms() - start_time
#                 print('Respuesta recibida desde', addr, 'en', elapsed_time, 'ms')
#                 return True  # Se recibió una respuesta
#                 break
#             elif time.ticks_ms() - start_time > 1000:
#                 print('Tiempo de espera agotado.')
#                 return False  # Tiempo de espera agotado sin respuesta
#                 break
#         icmp_socket.close()
    
    
    def is_wifi_connected():
        return wlan_sta.isconnected()

    def is_wifi_network_connected():
        if is_wifi_connected():
            pin_response = do_ping()
            print("Conectado a la red:", wlan_sta.config("essid"))
            print("ping('a google')", pin_response)
            if pin_response:
                print("Conexión a Internet establecida.")
                return True 
            else:
                print("Conexión a la red local pero sin acceso a Internet.")
                return False 
        else:
            print("No se ha podido conectar a la red.")
            return False 
            
    
    def handle_wifi_connection():
        while not is_wifi_network_connected():
            blinking_led()
            pass
    
    def set_leds_on_wifi_connected():
        led_wifi.on()
        led_web_server.off()
        
    #-------------
        
        
    def read_profiles():
        with open(NETWORK_PROFILES) as f:
            lines = f.readlines()
        profiles = {}
        for line in lines:
            ssid, password = line.strip("\n").split(";")
            profiles[ssid] = password
        return profiles


    def write_profiles(profiles):
        lines = []
        for ssid, password in profiles.items():
            lines.append("%s;%s\n" % (ssid, password))
        with open(NETWORK_PROFILES, "w") as f:
            f.write(''.join(lines))

    # Se conecta al wifi
    def do_connect(ssid, password, blinking_led=None, set_leds_on_wifi_connected=None):
        wlan_sta.active(True)
        if wlan_sta.isconnected():
            if(set_leds_on_wifi_connected):
                set_leds_on_wifi_connected()
            return None
        print('Trying to connect to %s...F' % ssid)
        print('ssid', ssid)
        print('password', password)
        wlan_sta.connect(ssid, password)
        for retry in range(200):
            connected = wlan_sta.isconnected()
            if connected:
                break
            blinking_led()
            if led_web_server:
                led_web_server.off()
            print('.', end='')
        if connected:
            print('\nConnected. Network config: ', wlan_sta.ifconfig())
            if led_wifi:
                led_wifi.on()
            
        else:
            print('\nFailed. Not Connected to: ' + ssid)
        return connected


    def send_header(client, status_code=200, content_length=None ):
        client.sendall("HTTP/1.0 {} OK\r\n".format(status_code))
        client.sendall("Content-Type: text/html\r\n")
        if content_length is not None:
          client.sendall("Content-Length: {}\r\n".format(content_length))
        client.sendall("\r\n")


    def send_response(client, payload, status_code=200):
        content_length = len(payload)
        send_header(client, status_code, content_length)
        if content_length > 0:
            client.sendall(payload)
        client.close()


    def handle_root(client):
        global wlan_sta
        wlan_sta.active(True)
        print('wlan_sta.scan()', wlan_sta.scan())
        print('network.WLAN(network.STA_IF).scan()', network.WLAN(network.STA_IF).scan())
        network.WLAN(network.STA_IF)
        ssids = sorted(ssid.decode('utf-8') for ssid, *_ in wlan_sta.scan())
        print("ssids",ssids)
        send_header(client)
        client.sendall("""\
            <html>
                <h1 style="color: #5e9ca0; text-align: center;">
                    <span style="color: #ff0000;">
                        Wi-Fi Client Setup
                    </span>
                </h1>
                <form action="configure" method="post">
                    <table style="margin-left: auto; margin-right: auto;">
                        <tbody>
        """)
        while len(ssids):
            ssid = ssids.pop(0)
            client.sendall("""\
                            <tr>
                                <td colspan="2">
                                    <input type="radio" name="ssid" value="{0}" />{0}
                                </td>
                            </tr>
            """.format(ssid))
        client.sendall("""\
                            <tr>
                                <td>Password:</td>
                                <td><input name="password" type="password" /></td>
                            </tr>
                        </tbody>
                    </table>
                    <p style="text-align: center;">
                        <input type="submit" value="Submit" />
                    </p>
                </form>
                <p>&nbsp;</p>
                <hr />
                <h5>
                    <span style="color: #ff0000;">
                        Your ssid and password information will be saved into the
                        "%(filename)s" file in your ESP module for future usage.
                        Be careful about security!
                    </span>
                </h5>
                <hr />
                <h2 style="color: #2e6c80;">
                    Some useful infos:
                </h2>
                <ul>
                    <li>
                        Original code from <a href="https://github.com/cpopp/MicroPythonSamples"
                            target="_blank" rel="noopener">cpopp/MicroPythonSamples</a>.
                    </li>
                    <li>
                        This code available at <a href="https://github.com/tayfunulu/WiFiManager"
                            target="_blank" rel="noopener">tayfunulu/WiFiManager</a>.
                    </li>
                </ul>
            </html>
        """ % dict(filename=NETWORK_PROFILES))
        client.close()


    def handle_configure(client, request):
        match = ure.search("ssid=([^&]*)&password=(.*)", request)
        
        if match is None:
            send_response(client, "Parameters not found", status_code=400)
            return False
        # version 1.9 compatibility
        try:
            ssid = match.group(1).decode("utf-8").replace("%3F", "?").replace("%21", "!").replace("%2C", ",")
            password = match.group(2).decode("utf-8").replace("%3F", "?").replace("%21", "!").replace("%2C", ",")
        except Exception:
            ssid = match.group(1).replace("%3F", "?").replace("%21", "!")
            password = match.group(2).replace("%3F", "?").replace("%21", "!")

        if len(ssid) == 0:
            send_response(client, "SSID must be provided", status_code=400)
            return False

        if do_connect(ssid, password, blinking_led, set_leds_on_wifi_connected):
            response = """\
                <html>
                    <center>
                        <br><br>
                        <h1 style="color: #5e9ca0; text-align: center;">
                            <span style="color: #ff0000;">
                                ESP successfully connected to WiFi network %(ssid)s.
                            </span>
                        </h1>
                        <br><br>
                    </center>
                </html>
            """ % dict(ssid=ssid)
            send_response(client, response)
            time.sleep(1)
            wlan_ap.active(False)
            try:
                profiles = read_profiles()
            except OSError:
                profiles = {}
            profiles[ssid] = password
            write_profiles(profiles)

            time.sleep(5)

            return True
        else:
            response = """\
                <html>
                    <center>
                        <h1 style="color: #5e9ca0; text-align: center;">
                            <span style="color: #ff0000;">
                                ESP could not connect to WiFi network %(ssid)s.
                            </span>
                        </h1>
                        <br><br>
                        <form>
                            <input type="button" value="Go back!" onclick="history.back()"></input>
                        </form>
                    </center>
                </html>
            """ % dict(ssid=ssid)
            send_response(client, response)
            return False


    def handle_not_found(client, url):
        send_response(client, "Path not found: {}".format(url), status_code=404)


    def stop():
        global server_socket

        if server_socket:
            server_socket.close()
            server_socket = None


    def start(led_web_server, port=80):
        global server_socket

        addr = usocket.getaddrinfo('0.0.0.0', port)[0][-1]

        stop()

        wlan_sta.active(True)
        wlan_ap.active(True)

        wlan_ap.config(essid=ap_ssid, password=ap_password, authmode=ap_authmode)

        server_socket = usocket.socket()
        server_socket.bind(addr)
        server_socket.listen(1)

        print('Connect to WiFi ssid ' + ap_ssid + ', default password: ' + ap_password)
        print('and access the ESP via your favorite web browser at 192.168.4.1.')
        print('Listening on:', addr)

        while True:
            if wlan_sta.isconnected():
                wlan_ap.active(False)
                return True
            led_web_server.on()
            client, addr = server_socket.accept()
            print('client connected from', addr)
            try:
                client.settimeout(5.0)

                request = b""
                try:
                    while "\r\n\r\n" not in request:
                        request += client.recv(512)
                except OSError:
                    pass

                # Handle form data from Safari on macOS and iOS; it sends \r\n\r\nssid=<ssid>&password=<password>
                try:
                    request += client.recv(1024)
                    print("Received form data after \\r\\n\\r\\n(i.e. from Safari on macOS or iOS)")
                except OSError:
                    pass

                print("Request is: {}".format(request))
                if "HTTP" not in request:  # skip invalid requests
                    continue

                # version 1.9 compatibility
                try:
                    url = ure.search("(?:GET|POST) /(.*?)(?:\\?.*?)? HTTP", request).group(1).decode("utf-8").rstrip("/")
                except Exception:
                    url = ure.search("(?:GET|POST) /(.*?)(?:\\?.*?)? HTTP", request).group(1).rstrip("/")
                print("URL is {}".format(url))

                if url == "":
                    handle_root(client)
                elif url == "configure":
                    handle_configure(client, request)
                else:
                    handle_not_found(client, url)

            finally:
                client.close()    
    
    #----------------

    # First check if there already is any connection:
    if wlan_sta.isconnected():
        return wlan_sta

    connected = False
    try:
        # ESP connecting to WiFi takes time, wait a bit and try again:
        time.sleep(1)
        if wlan_sta.isconnected():
            return wlan_sta

        # Read known network profiles from file
        profiles = read_profiles()

        # Search WiFis in range
        wlan_sta.active(True)
        networks = wlan_sta.scan()

        AUTHMODE = {0: "open", 1: "WEP", 2: "WPA-PSK", 3: "WPA2-PSK", 4: "WPA/WPA2-PSK"}
        for ssid, bssid, channel, rssi, authmode, hidden in sorted(networks, key=lambda x: x[3], reverse=True):
            ssid = ssid.decode('utf-8')
            encrypted = authmode > 0
            print("ssid: %s chan: %d rssi: %d authmode: %s" % (ssid, channel, rssi, AUTHMODE.get(authmode, '?')))
            if encrypted:
                if ssid in profiles:
                    password = profiles[ssid]
                    connected = do_connect(ssid, password, blinking_led, set_leds_on_wifi_connected)
#                     return (ssid, password)
                else:
                    print("skipping unknown encrypted network")
            else:  # open
#                 return None
                connected = do_connect(ssid, None, blinking_led, set_leds_on_wifi_connected)
            if connected:
                break

    except OSError as e:
        print("exception", str(e))

    # start web server for connection manager:
    if not connected:
        connected = start(led_web_server)
        
    wifi = (wlan_sta, is_wifi_connected, handle_wifi_connection, is_wifi_network_connected) if connected else None
    
    return wifi

            
def get_wifi():
    global wifi
    return wifi