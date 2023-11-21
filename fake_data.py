import serial
import time
import math

conn = serial.Serial("COM17")

val = 0
try:
    while True:
        conn.write((f"ALT {math.sin(val) + 1:.3f};").encode("ascii"))
        val += 0.1
        if val > 400:
            val = 0
        time.sleep(0.05)

finally:
    conn.close()
