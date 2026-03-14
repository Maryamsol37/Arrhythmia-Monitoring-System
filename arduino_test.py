import time
time.sleep(2)  # Wait after port openingimport serial
import serial.tools.list_ports


def test_arduino():
    print("Available ports:")
    for port in serial.tools.list_ports.comports():
        print(f"- {port.device}: {port.description}")
    
    try:
        print("\nAttempting COM5 connection...")
        with serial.Serial('COM5', 9600, timeout=2) as ard:
            print("Connection established, sending ping...")
            ard.write(b'P\n')  # Add newline
            
            print("Reading response...")
            response = ard.readline().decode().strip()
            print(f"Raw response: {repr(response)}")
            
            if response:
                print(f"Success! Arduino responded: {response}")
            else:
                print("No response received (check baud rate)")
                
    except Exception as e:
        print(f"\nError: {str(e)}")
        if "AccessDenied" in str(e):
            print("(Try closing Arduino IDE and other serial monitors)")

if __name__ == "__main__":
    test_arduino()