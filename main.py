from flask import Flask, render_template, jsonify
import serial
import threading
import re

app = Flask(__name__)

SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 115200
latest_uid = "Waiting for RFID..."

def read_rfid():
    global latest_uid
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
        while True:
            line = ser.readline().decode('utf-8').strip()
            if line.startswith("Card UID:"):
                uid_match = re.search(r'Card UID:\s*(.*)', line)
                if uid_match:
                    latest_uid = uid_match.group(1)
                    print("Extracted UID:", latest_uid)
    except Exception as e:
        latest_uid = f"Serial error: {e}"
        print("[ERROR]", e)

# Background thread to read RFID
threading.Thread(target=read_rfid, daemon=True).start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/uid')
def get_uid():
    return jsonify(uid=latest_uid)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
