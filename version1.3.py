#made the ip of the webpage print to the oled screen
from machine import Pin, SoftI2C
import network
import socket
import time
import _thread
from ssd1306 import SSD1306_I2C

# ------------------------------------------
# GPIO SWITCH SETUP
# ------------------------------------------

switch_pins = [13, 27, 25, 16, 17, 18, 19, 26]
switches = [Pin(pin, Pin.IN, Pin.PULL_DOWN) for pin in switch_pins]

# ------------------------------------------
# I2C OLED DISPLAY
# ------------------------------------------

i2c = SoftI2C(scl=Pin(22), sda=Pin(21))
oled = SSD1306_I2C(128, 64, i2c) 

# ------------------------------------------
# WIFI ACCESS POINT
# ------------------------------------------

def show_ip_on_oled(ip):
    oled.fill(0)
    oled.text("WiFi Ready!", 0, 0)
    oled.text("IP Address:", 0, 16)
    oled.text(ip, 0, 32)
    oled.show()
    time.sleep(3)




ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid="GenGodCalc", password="BinaryRulz")

print("Setting up AP...")
while not ap.active():
    pass
ip = ap.ifconfig()[0]
print("AP active! Connect to:", ip)

show_ip_on_oled(ip)


# ------------------------------------------
# BIT READING / CONVERSION
# ------------------------------------------

def read_bits():
    bits = []
    for sw in switches:
        bits.append(0 if sw.value() else 1)
    return bits

def bits_to_decimal(bits):
    return int("".join(str(b) for b in bits), 2)

# ------------------------------------------
# OLED UPDATE
# ------------------------------------------

def update_oled(bits, decimal):
    binary = "".join(str(b) for b in bits)
    oled.fill(0)
    oled.text("Binary:", 0, 0)
    oled.text(binary, 0, 12)
    oled.text("Decimal:", 0, 30)
    oled.text(str(decimal), 0, 42)
    oled.show()

# ------------------------------------------
# AJAX-ENABLED WEB SERVER
# ------------------------------------------

HTML_PAGE = """\
HTTP/1.1 200 OK
Content-Type: text/html

<!DOCTYPE html>
<html>
<head>
<title>Binary Calculator</title>
<style>
body { font-family: Arial; background:#222; color:#eee; }
.box { padding:20px; background:#333; width:300px; margin:auto;
       margin-top:40px; border-radius:10px; }
</style>
<script>
function update() {
    fetch("/json")
    .then(r => r.json())
    .then(data => {
        document.getElementById("bits").innerText = data.bits;
        document.getElementById("binary").innerText = data.binary;
        document.getElementById("decimal").innerText = data.decimal;
    });
}
setInterval(update, 300);
</script>
</head>
<body onload="update()">
<div class="box">
<h2>Binary Calculator</h2>
<p><b>Bits:</b> <span id="bits">...</span></p>
<p><b>Binary:</b> <span id="binary">...</span></p>
<p><b>Decimal:</b> <span id="decimal">...</span></p>
</div>
</body>
</html>
"""

def start_server():
    s = socket.socket()
    s.bind(("0.0.0.0", 80))
    s.listen(1)
    print("Web server running at http://{}".format(ap.ifconfig()[0]))

    while True:
        conn, addr = s.accept()
        request = conn.recv(1024).decode()

        # Determine the requested path
        try:
            path = request.split(" ")[1]
        except:
            conn.close()
            continue

        bits = read_bits()
        binary = "".join(str(b) for b in bits)
        decimal = bits_to_decimal(bits)

        if path == "/" or path == "/index.html":
            conn.send(HTML_PAGE)

        elif path == "/json":
            json = (
                'HTTP/1.1 200 OK\n'
                'Content-Type: application/json\n\n'
                f'{{"bits": {bits}, "binary": "{binary}", "decimal": {decimal}}}'
            )
            conn.send(json)

        conn.close()

# ------------------------------------------
# START THREADS
# ------------------------------------------

_thread.start_new_thread(start_server, ())

print("System ready. Live dashboard available.")

# ------------------------------------------
# MAIN LOOP: UPDATE OLED
# ------------------------------------------

while True:
    bits = read_bits()
    decimal = bits_to_decimal(bits)
    update_oled(bits, decimal)
    time.sleep(0.15)