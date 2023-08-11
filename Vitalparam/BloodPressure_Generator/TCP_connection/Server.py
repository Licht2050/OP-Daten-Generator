import socket


def process_blood_pressure_data(client_socket):
    try:
        while True:
            data = client_socket.recv(1024).decode()
            if not data:
                break
            data_value = data.split(",")
            if len(data_value) !=2:
                print("Invalid data format.")
                continue
            systolic, diastolic = map(int, data_value)

            print(f"Received data: Systolic: {systolic} mmHg, Distolic {diastolic} mmHg")

    except Exception as e:
        print("Data Consumer stopped with error: {e}")
    finally:
        client_socket.close()




if __name__ == "__main__":
    server_host = "localhost"
    server_port = 60000
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((server_host, server_port))
    server_socket.listen(1)


    print(f"Listening on {server_host}:{server_port}...")

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            print(f"Connection established with {client_address}.")
            process_blood_pressure_data(client_socket)
    except KeyboardInterrupt:
        print(f"Sever stopped.")

    finally:
        server_socket.close()
    
