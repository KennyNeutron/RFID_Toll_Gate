import serial
import time
import sys

def connect_to_serial_port(port='COM3', baud_rate=9600, timeout=1, max_attempts=3):
    """Attempt to connect to the serial port with retry logic."""
    for attempt in range(max_attempts):
        try:
            print(f"Attempt {attempt+1}/{max_attempts}: Connecting to {port}...")
            ser = serial.Serial(
                port=port,
                baudrate=baud_rate,
                timeout=timeout
            )
            print(f"Successfully connected to {port}")
            return ser
        except serial.SerialException as e:
            print(f"Error connecting to {port}: {e}")
            if "Access is denied" in str(e):
                print("The port may be in use by another application.")
                print("- Check if any other program is using the port")
                print("- Make sure you're running with administrator privileges")
                print("- Try restarting your computer to release the port")
            
            if attempt < max_attempts - 1:
                wait_time = 2 * (attempt + 1)  # Exponential backoff
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"Failed to connect to {port} after {max_attempts} attempts.")
                return None

# Example usage
if __name__ == "__main__":
    # Try to connect to the serial port
    ser = connect_to_serial_port(port='COM3')
    
    if ser:
        try:
            # Your code for communicating with the serial device
            print("Serial port is ready for communication")
            # Example: ser.write(b'Hello\n')
        except Exception as e:
            print(f"Error during communication: {e}")
        finally:
            # Always close the serial connection when done
            if ser.is_open:
                ser.close()
                print("Serial port closed")
    else:
        print("Unable to continue without serial connection")
        # Handle the case where the serial connection couldn't be established
        # Maybe use a fallback method or exit the program