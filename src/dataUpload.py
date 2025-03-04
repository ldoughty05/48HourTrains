import serial
import requests
import json
import html

SERIAL_PORT = "COM4"
BAUD_RATE = 9600 #115200
WEB_SERVER_URL = "http://127.0.0.1:5000/data"

ser = serial.Serial(SERIAL_PORT, BAUD_RATE)



def get_dict_from_serial(serial_data_string):
  try:
    print(f"Received Serial String: {serial_data_string}\n")
    print("vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv\n")
    decoded_serial_data_string = html.unescape(serial_data_string).strip('"""')
    serial_data_dict = json.loads(decoded_serial_data_string)
    print(f"Serial Data Dict: {serial_data_dict}\n")
    return serial_data_dict;     
  except Exception as e:
    print(f"Error getting JSON from Serial:\n{e}")
    return None

def tryReadSerial():
  if ser.in_waiting > 0:
    serial_data_string = ser.readline().decode().strip()
    data_dict = get_dict_from_serial(serial_data_string)


if __name__ == "__main__":
  while True:
    if ser.in_waiting > 0:
      serial_data_string = ser.readline().decode().strip()
      # Check that the serial is in the shape of a json.
      data_dict = get_dict_from_serial(serial_data_string)
      if (data_dict):
        headers = {"Content-Type": "application/json"}
        response = requests.post(WEB_SERVER_URL, json=data_dict, headers=headers)
        print(f"Server Response: {response.text}\n")
        print(f"=========================================\n")



