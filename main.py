from flask import Flask, render_template, jsonify, request, redirect
import serial
import threading
import sqlite3
from datetime import datetime
from collections import defaultdict
import time

app = Flask(__name__)

SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 9600
latest_data = {
    "rfid": "Waiting...",
    "transaction_type": "Waiting..."
}

# ✅ Periodically send vehicle counts over serial
def send_vehicle_counts():
    def send_loop():
        while True:
            try:
                ser_out = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
                time.sleep(2)  # Let Arduino reset
                conn = sqlite3.connect('rfid_gate.db')
                c = conn.cursor()
                today = datetime.now().strftime("%Y-%m-%d")
                c.execute('''
                    SELECT vehicle_type, entry_type
                    FROM logs
                    WHERE DATE(timestamp) = ?
                ''', (today,))
                logs = c.fetchall()
                conn.close()

                counts = defaultdict(int)
                for vehicle_type, entry_type in logs:
                    key = vehicle_type.strip().lower()
                    if entry_type == 'enter':
                        counts[key] += 1
                    elif entry_type == 'exit':
                        counts[key] -= 1

                motorcycles = max(counts.get("motorcycle", 0), 0)
                cars = max(counts.get("car", 0), 0)

                serial_data = f"SM:{motorcycles},C:{cars}\n"
                ser_out.write(serial_data.encode('utf-8'))
                print(f"Serial Data Sent to Serial: {serial_data.strip()}")

                time.sleep(0.2)
                while ser_out.in_waiting:
                    response = ser_out.readline().decode('utf-8', errors='ignore').strip()
                    print("[Arduino RX]:", response)

                ser_out.close()
            except Exception as e:
                print("[ERROR - send_vehicle_counts]:", e)

            time.sleep(3)  # Wait 3 seconds before repeating

    threading.Thread(target=send_loop, daemon=True).start()


# ✅ Logging function
def log_transaction(rfid, entry_type):
    try:
        conn = sqlite3.connect('rfid_gate.db')
        c = conn.cursor()

        # ✅ Check the latest entry_type for this RFID
        c.execute('''
            SELECT entry_type FROM logs
            WHERE rfid = ?
            ORDER BY timestamp DESC
            LIMIT 1
        ''', (rfid,))
        last_entry = c.fetchone()

        # ✅ Skip if same as last entry_type
        if last_entry and last_entry[0] == entry_type:
            print(f"[SKIPPED] Duplicate entry_type '{entry_type}' for RFID {rfid}")
            conn.close()
            return

        # ✅ Fetch user details
        c.execute("SELECT name, course, year_level, vehicle_type, plate_number FROM users WHERE rfid = ?", (rfid,))
        result = c.fetchone()

        if result:
            name, course, year_level, vehicle_type, plate_number = result
        else:
            name = f"UNKNOWN: {rfid}"
            course = year_level = vehicle_type = plate_number = ""

        # ✅ Insert new log
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute('''
            INSERT INTO logs (
                rfid, name, course, year_level, vehicle_type,
                plate_number, timestamp, entry_type
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            rfid, name, course, year_level, vehicle_type,
            plate_number, timestamp, entry_type
        ))

        conn.commit()
        conn.close()

        print(f"[LOGGED] {name} ({rfid}) | {entry_type} @ {timestamp}")
        send_vehicle_counts()

    except Exception as e:
        print("[ERROR - logging]:", e)


# ✅ Serial reading + logging
def read_rfid():
    global latest_data
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

                        transaction = "enter" if role == 1 else "exit" if role == 2 else "unknown"
                        latest_data = {
                            "rfid": uid,
                            "transaction_type": transaction
                        }

                        if transaction in ["enter", "exit"]:
                            log_transaction(uid, transaction)
                        print("Extracted UID & Role:", uid, "|", transaction)

                except Exception as e:
                    print("[Parse Error]", e)

    except Exception as e:
        latest_data["rfid"] = "Serial Error"
        latest_data["transaction_type"] = "Serial Error"
        print("[ERROR - serial]:", e)

# ✅ Background thread
threading.Thread(target=read_rfid, daemon=True).start()
send_vehicle_counts()


# ✅ Web routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/uid')
def get_uid():
    return jsonify(latest_data)

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
    selected_date = request.args.get('date')
    conn = sqlite3.connect('rfid_gate.db')
    c = conn.cursor()

    if selected_date:
        c.execute('''
            SELECT rfid, name, course, year_level, vehicle_type, plate_number, timestamp, entry_type
            FROM logs
            WHERE DATE(timestamp) = ?
            ORDER BY timestamp DESC
        ''', (selected_date,))
    else:
        c.execute('''
            SELECT rfid, name, course, year_level, vehicle_type, plate_number, timestamp, entry_type
            FROM logs
            ORDER BY timestamp DESC
        ''')

    logs_data = c.fetchall()
    conn.close()
    return render_template('logs.html', logs=logs_data, selected_date=selected_date)

@app.route('/delete_logs/<date>', methods=['POST'])
def delete_logs(date):
    try:
        conn = sqlite3.connect('rfid_gate.db')
        c = conn.cursor()
        c.execute("DELETE FROM logs WHERE DATE(timestamp) = ?", (date,))
        conn.commit()
        conn.close()
        print(f"[DELETED] Logs for {date}")
    except Exception as e:
        print(f"[ERROR] Failed to delete logs for {date}: {e}")
    return redirect('/logs?date=' + date)

@app.route('/latest_transaction')
def latest_transaction():
    try:
        conn = sqlite3.connect('rfid_gate.db')
        c = conn.cursor()
        c.execute('''
            SELECT name, course, year_level, vehicle_type, plate_number,
                   timestamp, entry_type
            FROM logs
            ORDER BY timestamp DESC
            LIMIT 1
        ''')
        row = c.fetchone()
        conn.close()

        if row:
            return jsonify({
                "name": row[0],
                "course": row[1],
                "year_level": row[2],
                "vehicle_type": row[3],
                "plate_number": row[4],
                "timestamp": row[5],
                "entry_type": row[6]
            })
        else:
            return jsonify({"status": "no_logs"})
    except Exception as e:
        print("[ERROR] latest_transaction:", e)
        return jsonify({"status": "error"})

@app.route('/delete_user/<rfid>', methods=['POST'])
def delete_user(rfid):
    try:
        conn = sqlite3.connect('rfid_gate.db')
        c = conn.cursor()
        c.execute("DELETE FROM users WHERE rfid = ?", (rfid,))
        conn.commit()
        conn.close()
        print(f"[DELETED USER] RFID: {rfid}")
    except Exception as e:
        print(f"[ERROR] Failed to delete user {rfid}: {e}")
    return redirect('/users')

@app.route('/current_counts')
def current_counts():
    try:
        conn = sqlite3.connect('rfid_gate.db')
        c = conn.cursor()
        today = datetime.now().strftime("%Y-%m-%d")

        c.execute('''
            SELECT vehicle_type, entry_type
            FROM logs
            WHERE DATE(timestamp) = ?
        ''', (today,))

        logs = c.fetchall()
        conn.close()

        counts = defaultdict(int)
        for vehicle_type, entry_type in logs:
            key = vehicle_type.strip().lower()
            if entry_type == 'enter':
                counts[key] += 1
            elif entry_type == 'exit':
                counts[key] -= 1

        return jsonify({
            "motorcycles": max(counts.get("motorcycle", 0), 0),
            "cars": max(counts.get("car", 0), 0)
        })

    except Exception as e:
        print("[ERROR] current_counts:", e)
        return jsonify({"motorcycles": 0, "cars": 0, "status": "error"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
