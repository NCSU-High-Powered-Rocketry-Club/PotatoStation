import serial
import time
import math

conn = serial.Serial("COM17", timeout=3, write_timeout=0)
conn2 = serial.Serial("COM23", timeout=3, write_timeout=0)

val = 0
curtime = 0
try:
    while True:
        # empty da read buffers
        conn.read_all()
        conn2.read_all()

        conn.write((f"ALT {100*(math.sin(val/2) + 1):.3f};").encode("ascii"))
        conn.write((f"MTR {(math.sin(val/2)+1) * 50:.3f};").encode("ascii"))
        conn.write((f"TEMP {(math.sin(val/4)+1) * 50:.3f};").encode("ascii"))
        conn.write((f"VELO {(math.sin(val/2)) * 50:.3f};").encode("ascii"))

        if (time.time() - curtime) > 2:
            conn2.write((f"MSG hi;").encode("ascii"))
            curtime = time.time()
        val += 0.1
        if val > 400:
            val = 0
        time.sleep(0.05)

finally:
    conn.close()
    conn2.close()
