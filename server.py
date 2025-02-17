import socket
import threading
import pickle

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen(5)
        self.clients = []
        self.player_positions = {}
        print("Server started, waiting for clients...")

    def handle_client(self, client_socket, client_address):
        print(f"New connection from {client_address}")
        try:
            while True:
                data_length_bytes = client_socket.recv(4)
                if not data_length_bytes:
                    print(f"Client {client_address} disconnected.")
                    break

                data_length = int.from_bytes(data_length_bytes, byteorder='big')
                if data_length == 0:
                    continue  # Ignore empty data

                # Receive full data
                data = b""
                while len(data) < data_length:
                    chunk = client_socket.recv(data_length - len(data))
                    if not chunk:
                        print("Connection lost while receiving data.")
                        return
                    data += chunk

                # Unpickle the received data
                try:
                    player_data = pickle.loads(data)
                except pickle.UnpicklingError:
                    print("Failed to unpickle data.")
                    continue

                # Store the updated player data
                self.player_positions[client_address] = player_data

                # Broadcast updated data **except to the sender**
                players_data = pickle.dumps(self.player_positions)
                for client in self.clients:
                    if client != client_socket:  # Do not send to the sender
                        try:
                            client.sendall(len(players_data).to_bytes(4, byteorder='big'))
                            client.sendall(players_data)
                        except Exception as e:
                            print(f"Failed to send data to {client}: {e}")

        except Exception as e:
            print(f"Error with client {client_address}: {e}")
        finally:
            client_socket.close()
            if client_socket in self.clients:
                self.clients.remove(client_socket)
            self.player_positions.pop(client_address, None)

    def accept_connections(self):
        while True:
            client_socket, client_address = self.server_socket.accept()
            print(f"Client {client_address} connected")
            self.clients.append(client_socket)
            threading.Thread(target=self.handle_client, args=(client_socket, client_address), daemon=True).start()

if __name__ == "__main__":
    server = Server('127.0.0.1', 12345)
    server.accept_connections()
