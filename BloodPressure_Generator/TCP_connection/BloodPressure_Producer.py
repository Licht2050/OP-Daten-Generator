import random
import time
import socket

def generate_random_blood_pressure():
    systolic = random.randint(90, 140)
    diastolic = random.randint(60, 90)
    return systolic, diastolic

def display_blood_pressure(systolic, diastolic):
    print(f"Systolic: {systolic} mmHg, Diastolic: {diastolic} mmHg")

def simulate_blood_pressure_stream(interval_seconds=5):
    try:
        while True:
            systolic, diastolic = generate_random_blood_pressure()
            display_blood_pressure(systolic, diastolic)
            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        print("Simulation stopped.")

def send_blood_pressure_data(host, port, interval_seconds=5):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        while True:
            systolic, diastolic = generate_random_blood_pressure()
            data = f"{systolic}, {diastolic}"
            client_socket.sendall(data.encode())
            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        print("Simulation stopped.")
    finally:
        client_socket.close()


if __name__ == "__main__":
    server_host = "localhost"
    server_port = 60000

    send_blood_pressure_data(server_host, server_port)

# Beispielaufruf:
# simulate_blood_pressure_stream()
