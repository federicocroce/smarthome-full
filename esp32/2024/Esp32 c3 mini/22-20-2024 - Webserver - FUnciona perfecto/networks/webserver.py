from libs.microdot.microdot import Microdot, Response
from libs.microdot.utemplate import Template
import ujson as json
import network
from utilities.common import update_core_data, get_core_data, reset_device


Template.initialize('libs/microdot/templates')

# Escanear redes WiFi disponibles
def scan_wifi_networks():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    networks = wlan.scan()
    print("scan_wifi_networks", networks)
    ssids = []
    for current_network in networks:
        ssids.append(current_network[0].decode("utf-8"))
    return ssids


# Configurar el ESP32 como Access Point con IP estática
def create_access_point(ssid, password):
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid=ssid, password=password)

    # Configurar una IP estática para el Access Point
    ap.ifconfig(('192.168.4.1', '255.255.255.0', '192.168.4.1', '8.8.8.8'))

    # Esperar a que el Access Point esté activo
    while not ap.active():
        pass

    print(f"Access Point '{ssid}' creado.")
    print("IP:", ap.ifconfig()[0])
    return ap.ifconfig()[0]  # Retorna la IP del AP



app = Microdot()
Response.default_content_type = 'text/html'


@app.route('/', methods=['GET', 'POST'])
async def index(req):
    networks = scan_wifi_networks()
    print("networks", networks)
#     if req.method == 'POST':
#         name = req.form.get('name')
    return Template('index.html').render(networks=networks)


# Ruta para procesar el formulario y guardar el nombre en un archivo JSON
@app.route('/save', methods=['POST'])
def save_device_name(request):
    device_name = request.form.get('device_name', '')
    ssid = request.form.get('ssid', '')
    password = request.form.get('password', '')
    
    data = {}
    
    if device_name:
        data["name"] = device_name
    if ssid:
        data["ssid"] = ssid
    if password:
        data["password"] = password
    
#     data = {"name": device_name, "ssid": ssid, "password": password}
    
    update_core_data(data)
    return 'dispositivo guardado correctamente.'



def run_web_server():
    #     
    print("Empieza")
    # Leer los datos del archivo JSON
    core_data = get_core_data()
    print("Continua")
    # Verificar si los datos fueron leídos correctamente y obtener el nombre
    if core_data:
        prev_ssid = core_data.get('name', "ESP32")
    else:
        prev_ssid = "ESP32"

    # Crear el SSID basado en el nombre anterior
    ssid = prev_ssid + '_AccessPoint'
    password = "12345678"  # Debe tener al menos 8 caracteres
    ip_address = create_access_point(ssid, password)

    # Ejecutar el servidor en la IP del Access Point
    app.run(host=ip_address, port=80)



# # Ruta para la página principal con el formulario HTML
# @app.route('/')
# def index(request):
#      # Escanear las redes WiFi disponibles
#     networks = scan_wifi_networks()
#         
#     html = f"""
#     <html>
#         <body>
#             <h2>Configurar Nombre del Dispositivo</h2>
#             <form action="/save" method="post">
#                 <label for="device_name">Nombre del Dispositivo:</label><br>
#                 <input type="text" id="device_name" name="device_name"><br><br>
#                 
#                 <div>
#                     <p>Redes WIFI disponibiles:</p>
#                     
#                     {% for network in networks %}
#                         <input type="radio" id="network-{{ network }}" name="networks" value="{{ network }}">
#                         <label for="network-{{ network }}">{{ option }}</label><br>
#                     {% endfor %}
#                     
#                 </div>
#                 
#                 <input type="submit" value="Guardar">
#             </form>
#         </body>
#     </html>
#     """
#     
#     return Response(body=html, headers={'Content-Type': 'text/html'})




