from flask import Flask, render_template, jsonify, request, redirect
import serial
import threading
import re
import sqlite3

app = Flask(__name__)

SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 9600
latest_uid = "Waiting for RFID..."

def read_rfid():
    global latest_uid
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
        while True:
            line = ser.readline().decode('utf-8').strip()
            if line.startswith("Role:"):
                try:
                    role = int(line.split(":")[1].strip())
                    uid_line = ser.readline().decode('utf-8').strip()
                    if uid_line.startswith("UID:"):
                        uid = uid_line.split(":")[1].strip()
                        latest_uid = f"{uid} {role}"
                        print("Extracted UID & Role:", latest_uid)
                except Exception as e:
                    print("[Parse Error]", e)

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
    try:
        uid, role = latest_uid.strip().split()
        role = int(role)
        transaction = "Entry" if role == 1 else "Exit" if role == 2 else "Unknown"
        return jsonify(rfid=uid, transaction_type=transaction)
    except Exception:
        return jsonify(rfid="N/A", transaction_type="N/A")




@app.route('/register', methods=['GET', 'POST'])
def register():
    message = None

    if request.method == 'POST':
        rfid = request.form['rfid'].strip()
        name = request.form['name'].strip()
        course = request.form['course'].strip()
        year_level = request.form['year_level'].strip()
        vehicle_type = request.form['vehicle_type'].strip()
        plate_number = request.form['plate_number'].strip()

        try:
            conn = sqlite3.connect('rfid_gate.db')
            c = conn.cursor()
            c.execute('''
                INSERT INTO users (rfid, name, course, year_level, vehicle_type, plate_number)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (rfid, name, course, year_level, vehicle_type, plate_number))
            conn.commit()
            conn.close()
            message = f"User '{name}' registered successfully!"
        except sqlite3.IntegrityError:
            message = f"RFID '{rfid}' already exists!"
        except Exception as e:
            message = f"Error: {e}"

    return render_template('register.html', message=message)

@app.route('/users')
def users():
    conn = sqlite3.connect('rfid_gate.db')
    c = conn.cursor()
    c.execute('''
    SELECT rfid, name, course, year_level, vehicle_type, plate_number
    FROM users ORDER BY name
''')
    user_list = c.fetchall()
    conn.close()
    return render_template('users.html', users=user_list)

@app.route('/logs')
def logs():
    selected_date = request.args.get('date')  # from query parameter
    conn = sqlite3.connect('rfid_gate.db')
    c = conn.cursor()

    if selected_date:
        c.execute("SELECT rfid, name, course, year_level, vehicle_type, plate_number, timestamp, entry_type FROM logs WHERE DATE(timestamp) = ? ORDER BY timestamp DESC", (selected_date,))
    else:
        c.execute("SELECT rfid, name, course, year_level, vehicle_type, plate_number, timestamp, entry_type FROM logs ORDER BY timestamp DESC")

    logs_data = c.fetchall()
    conn.close()
    return render_template('logs.html', logs=logs_data, selected_date=selected_date)



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
