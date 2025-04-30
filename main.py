from flask import Flask, render_template, jsonify, request, redirect
import serial
import threading
import sqlite3
from datetime import datetime
from collections import defaultdict
import time

app = Flask(__name__)

SERIAL_PORT = 'COM3'
BAUD_RATE = 9600

# Global variables
latest_data = {
    "rfid": "Waiting...",
    "transaction_type": "Waiting..."
}

# Global serial connection (shared between threads)
serial_lock = threading.Lock()
serial_connection = None

# Initialize serial connection
def init_serial():
    global serial_connection
    try:
        if serial_connection is None or not serial_connection.is_open:
            serial_connection = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
            time.sleep(2)  # Let Arduino reset after connection
            print(f"Serial connection to {SERIAL_PORT} established")
        return True
    except Exception as e:
        print(f"[ERROR - init_serial]: {e}")
        return False

# Safe serial read function with lock
def safe_serial_read():
    global serial_connection
    with serial_lock:
        if not init_serial():
            return None
        try:
            line = serial_connection.readline().decode('utf-8', errors='ignore').strip()
            return line
        except Exception as e:
            print(f"[ERROR - serial_read]: {e}")
            return None

# Optimized serial write function with lock
def safe_serial_write(data):
    global serial_connection
    with serial_lock:
        if not init_serial():
            return False
        try:
            serial_connection.write(data.encode('utf-8'))
            # Reduced sleep time to improve responsiveness
            time.sleep(0.1)  # Reduced from 0.2
            
            # Limit the amount of response reading to avoid long lock times
            max_reads = 5  # Limit the maximum number of reads
            read_count = 0
            responses = []
            while serial_connection.in_waiting and read_count < max_reads:
                response = serial_connection.readline().decode('utf-8', errors='ignore').strip()
                responses.append(response)
                read_count += 1
                
            if responses:
                print("[Arduino RX]:", responses)
            return True
        except Exception as e:
            print(f"[ERROR - serial_write]: {e}")
            return False

# Optimized vehicle counts sender
def send_vehicle_counts():
    def send_loop():
        while True:
            try:
                # Create a new connection in this thread
                with sqlite3.connect('rfid_gate.db') as conn:
                    c = conn.cursor()
                    today = datetime.now().strftime("%Y-%m-%d")
                    c.execute('''
                        SELECT vehicle_type, entry_type
                        FROM logs
                        WHERE DATE(timestamp) = ?
                    ''', (today,))
                    logs = c.fetchall()
                
                counts = defaultdict(int)
                for vehicle_type, entry_type in logs:
                    key = vehicle_type.strip().lower() if vehicle_type else ""
                    if entry_type == 'enter':
                        counts[key] += 1
                    elif entry_type == 'exit':
                        counts[key] -= 1

                motorcycles = max(counts.get("motorcycle", 0), 0)
                cars = max(counts.get("car", 0), 0)

                serial_data = f"SM:{motorcycles},C:{cars}\n"
                if safe_serial_write(serial_data):
                    print(f"Serial Data Sent: {serial_data.strip()}")
            except Exception as e:
                print("[ERROR - send_vehicle_counts]:", e)

            # Slightly longer sleep to reduce contention with RFID reader
            time.sleep(1.5)  # Adjusted sleep time

    # Start the send_loop in a daemon thread
    thread = threading.Thread(target=send_loop, daemon=True)
    thread.name = "VehicleCountSender"  # Named threads are easier to debug
    thread.start()
    return thread

# Logging function with context manager for database
def log_transaction(rfid, entry_type):
    try:
        with sqlite3.connect('rfid_gate.db') as conn:
            c = conn.cursor()

            # Check the latest entry_type for this RFID
            c.execute('''
                SELECT entry_type FROM logs
                WHERE rfid = ?
                ORDER BY timestamp DESC
                LIMIT 1
            ''', (rfid,))
            last_entry = c.fetchone()

            # Skip if same as last entry_type
            if last_entry and last_entry[0] == entry_type:
                print(f"[SKIPPED] Duplicate entry_type '{entry_type}' for RFID {rfid}")
                return

            # Fetch user details
            c.execute("SELECT name, course, year_level, vehicle_type, plate_number FROM users WHERE rfid = ?", (rfid,))
            result = c.fetchone()

            if result:
                name, course, year_level, vehicle_type, plate_number = result
            else:
                name = f"UNKNOWN: {rfid}"
                course = year_level = vehicle_type = plate_number = ""

            # Insert new log
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
            print(f"[LOGGED] {name} ({rfid}) | {entry_type} @ {timestamp}")

    except Exception as e:
        print("[ERROR - logging]:", e)

# Improved RFID reader with better error handling
def read_rfid():
    global latest_data
    
    def rfid_loop():
        while True:
            try:
                if init_serial():
                    line = safe_serial_read()
                    if line and line.startswith("Role:"):
                        try:
                            role = int(line.split(":")[1].strip())
                            
                            # Set a timeout for waiting for the UID
                            start_time = time.time()
                            uid_line = None
                            while time.time() - start_time < 1.0:  # 1 second timeout
                                uid_line = safe_serial_read()
                                if uid_line and uid_line.startswith("UID:"):
                                    break
                                time.sleep(0.05)  # Short sleep between attempts
                                
                            if uid_line and uid_line.startswith("UID:"):
                                uid = uid_line.split(":")[1].strip()

                                transaction = "enter" if role == 1 else "exit" if role == 2 else "unknown"
                                latest_data = {
                                    "rfid": uid,
                                    "transaction_type": transaction
                                }

                                if transaction in ["enter", "exit"]:
                                    log_transaction(uid, transaction)
                                print("Extracted UID & Role:", uid, "|", transaction)
                            else:
                                print("[WARNING] UID not received after Role")

                        except Exception as e:
                            print("[Parse Error]", e)
                else:
                    time.sleep(5)  # Wait before retry if connection failed
                    
            except Exception as e:
                latest_data["rfid"] = "Serial Error"
                latest_data["transaction_type"] = "Serial Error"
                print("[ERROR - read_rfid]:", e)
                time.sleep(5)  # Wait before retry
            
            # Short sleep to keep responsive but not hog CPU
            time.sleep(0.1)
    
    # Start the loop in a thread and return the thread object
    thread = threading.Thread(target=rfid_loop, daemon=True)
    thread.name = "RFIDReader"
    thread.start()
    return thread

# Web routes
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
            with sqlite3.connect('rfid_gate.db') as conn:
                c = conn.cursor()
                c.execute('''
                    INSERT INTO users (rfid, name, course, year_level, vehicle_type, plate_number)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (rfid, name, course, year_level, vehicle_type, plate_number))
                conn.commit()
                message = f"User '{name}' registered successfully!"
        except sqlite3.IntegrityError:
            message = f"RFID '{rfid}' already exists!"
        except Exception as e:
            message = f"Error: {e}"

    return render_template('register.html', message=message)

@app.route('/users')
def users():
    with sqlite3.connect('rfid_gate.db') as conn:
        c = conn.cursor()
        c.execute('''
            SELECT rfid, name, course, year_level, vehicle_type, plate_number
            FROM users ORDER BY name
        ''')
        user_list = c.fetchall()
    return render_template('users.html', users=user_list)

@app.route('/logs')
def logs():
    selected_date = request.args.get('date')
    with sqlite3.connect('rfid_gate.db') as conn:
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
    return render_template('logs.html', logs=logs_data, selected_date=selected_date)

@app.route('/delete_logs/<date>', methods=['POST'])
def delete_logs(date):
    try:
        with sqlite3.connect('rfid_gate.db') as conn:
            c = conn.cursor()
            c.execute("DELETE FROM logs WHERE DATE(timestamp) = ?", (date,))
            conn.commit()
            print(f"[DELETED] Logs for {date}")
    except Exception as e:
        print(f"[ERROR] Failed to delete logs for {date}: {e}")
    return redirect('/logs?date=' + date)

@app.route('/latest_transaction')
def latest_transaction():
    try:
        with sqlite3.connect('rfid_gate.db') as conn:
            c = conn.cursor()
            c.execute('''
                SELECT name, course, year_level, vehicle_type, plate_number,
                       timestamp, entry_type
                FROM logs
                ORDER BY timestamp DESC
                LIMIT 1
            ''')
            row = c.fetchone()

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
        with sqlite3.connect('rfid_gate.db') as conn:
            c = conn.cursor()
            c.execute("DELETE FROM users WHERE rfid = ?", (rfid,))
            conn.commit()
            print(f"[DELETED USER] RFID: {rfid}")
    except Exception as e:
        print(f"[ERROR] Failed to delete user {rfid}: {e}")
    return redirect('/users')

@app.route('/current_counts')
def current_counts():
    try:
        with sqlite3.connect('rfid_gate.db') as conn:
            c = conn.cursor()
            today = datetime.now().strftime("%Y-%m-%d")

            c.execute('''
                SELECT vehicle_type, entry_type
                FROM logs
                WHERE DATE(timestamp) = ?
            ''', (today,))

            logs = c.fetchall()

        counts = defaultdict(int)
        for vehicle_type, entry_type in logs:
            key = vehicle_type.strip().lower() if vehicle_type else ""
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
    # Start background threads - only start them here, not at module level
    rfid_thread = read_rfid()  # This now returns the thread object
    count_thread = send_vehicle_counts()  # This now returns the thread object
    
    # Run Flask app with debug mode off to avoid port conflicts
    app.run(debug=False, host='0.0.0.0', port=5000)