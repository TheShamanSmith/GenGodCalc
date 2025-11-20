# made the IP of the webpage print to the OLED screen
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
switches = [Pin(pin, Pin.IN) for pin in switch_pins]

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
    return [sw.value() for sw in switches]

def bits_to_decimal(bits):
    return int("".join(str(b) for b in bits), 2)

def decimal_to_hex(value):
    return hex(value)[2:].upper()  # Remove '0x' and uppercase

# ------------------------------------------
# OLED UPDATE (COMPACT)
# ------------------------------------------
def update_oled(bits, decimal):
    binary = "".join(str(b) for b in bits)
    hex_value = decimal_to_hex(decimal)
    dec_str = str(decimal)

    oled.fill(0)

    # Top line: Binary
    oled.text("Bin:", 0, 0)
    oled.text(binary, 40, 0)

    # Middle line: Hex
    oled.text("Hex:", 0, 20)
    oled.text(hex_value, 40, 20)

    # Bottom line: Decimal
    oled.text("Dec:", 0, 40)
    oled.text(dec_str, 40, 40)

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
        document.getElementById("hex").innerText = data.hex;
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
<p><b>Hex:</b> <span id="hex">...</span></p>
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
        hex_value = decimal_to_hex(decimal)

        if path == "/" or path == "/index.html":
            conn.send(HTML_PAGE)

        elif path == "/json":
            json = (
                'HTTP/1.1 200 OK\n'
                'Content-Type: application/json\n\n'
                f'{{"bits": {bits}, "binary": "{binary}", "decimal": {decimal}, "hex": "{hex_value}"}}'
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
