import serial

ser = serial.Serial('COM3', 115200, timeout=1)
print("Reading raw quaternion. Move the BNO and watch which values change.")
print("Format: i, j, k, real")

while True:
    try:
        line = ser.readline().decode('utf-8').strip()
        parts = line.split(',')
        if len(parts) >= 4:
            print(f"i={float(parts[0]):+.2f}  j={float(parts[1]):+.2f}  k={float(parts[2]):+.2f}  real={float(parts[3]):+.2f}")
    except KeyboardInterrupt:
        break
    except:
        pass