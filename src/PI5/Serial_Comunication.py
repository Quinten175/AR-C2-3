import serial
import time
import sys

# Configure the serial port used for Pi UART (use /dev/serial0 for canonical mapping)
PORT = '/dev/ttyAMA0'  # change to '/dev/ttyAMA0' if your setup requires it
BAUD = 115600

def send_command(cmd: str):
    ser = serial.Serial(PORT, BAUD, timeout=1)
    
    time.sleep(0.1)
    ser.reset_input_buffer()
    ser.write((cmd + '\n').encode('utf-8'))
    ser.flush()
    

    time.sleep(0.1)
    if ser.in_waiting > 0:
        print(ser.readline().decode('utf-8', errors='replace').rstrip())
    ser.close()

if __name__ == '__main__':
    pass

    