This is a simple binary calculator. It reads input from 8 physical switches and maps them to a binary string. It then prints the output to a self-hosted webpage and an attached oled screen.
Setup is fairly simple, uplaod this to the esp32 or similair device capable of running python. You will have to connect switches to the device in the exact order as in the code or it will not function the way you want.
an i2c library was also used in this script that you may need to download to your device or substitute with one you prefer. The wifi setting may also be changed to your liking.
beyond that enjoy!
