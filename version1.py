from machine import Pin, I2C
import network
import socket
import time
from ssd1306 import SSD1306_I2C

# -----------------------------
# GPIO SWITCH SETUP
# -----------------------------

switch_pins = [2, 3, 4, 5, 18, 19, 23, 25]   # safer pins for ESP32
switches = [Pin(pin, Pin.IN, Pin.PULL_UP) for pin in switch_pins]

# -----------------------------
# OLED DISPLAY (SSD1306)
# -----------------------------

i2c = I2C(0, scl=Pin(22), sda=Pin(21))
oled = SSD1306_I2C(128, 64, i2c)

# -----------------------------
# WIFI ACCESS POINT
# -----------------------------

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid="BinaryCalc", password="12345678")

print("Creating WiFi AP...")
while not ap.active():
    pass
print("AP active! Connect to:", ap.ifconfig()[0])

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------

def read_bits():
    """Reads all 8 switches: 1=closed, 0=open."""
    bits = []
    for sw in switches:
        # Switch pressed = LOW = 1
        bits.append(0 if sw.value() else 1)
    bits.reverse()  # MSB on left
    return bits

def bits_to_decimal(bits):
    return int("".join(str(b) for b in bits), 2)

def update_oled(bits, decimal):
    binary = "".join(str(b) for b in bits)
    oled.fill(0)
    oled.text("Binary:", 0, 0)
    oled.text(binary, 0, 12)
    oled.text("Decimal:", 0, 30)
    oled.text(str(decimal), 0, 42)
    oled.show()

# -----------------------------
# SIMPLE WEB SERVER
# -----------------------------

def start_server():
    html = """\
HTTP/1.1 200 OK

<html>
<head><title>Binary Calculator</title></head>
<body>
<h1>Binary Calculator</h1>
<p><b>Bits:</b> {bits}</p>
<p><b>Binary:</b> {binary}</p>
<p><b>Decimal:</b> {decimal}</p>
</body>
</html>
"""

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", 80))
    s.listen(1)
    print("Web server running on http://", ap.ifconfig()[0])

    while True:
        conn, addr = s.accept()
        request = conn.recv(1024)

        bits = read_bits()
        binary = "".join(str(b) for b in bits)
        decimal = bits_to_decimal(bits)

        response = html.format(bits=bits, binary=binary, decimal=decimal)
        conn.send(response)
        conn.close()

# -----------------------------
# MAIN LOOP
# -----------------------------

import _thread

# Start the webserver in another thread
_thread.start_new_thread(start_server, ())

print("System ready.")

# Update OLED continuously
while True:
    bits = read_bits()
    decimal = bits_to_decimal(bits)
    update_oled(bits, decimal)
    time.sleep(0.15)
