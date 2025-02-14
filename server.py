import socket
import threading
import pickle
import time

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen(5)
        self.clients = []
        self.player_positions = {}

    def handle_client(self, client_socket, client_address):
        print(f"New connection from {client_address}")
        try:
            while True:
                data_length = client_socket.recv(4)
                if not data_length:
                    break
                data_length = int.from_bytes(data_length, byteorder='big')

                data = b""
                while len(data) < data_length:
                    chunk = client_socket.recv(data_length - len(data))
                    if not chunk:
                        break
                    data += chunk

                player_data = pickle.loads(data)
                self.player_positions[client_address] = player_data  # Store player position and bullets

                print(f"Updated positions: {self.player_positions}")  # Debugging

                # Send updated positions and bullets to all clients
                players_data = pickle.dumps(self.player_positions)
                print(f"Sending player data: {self.player_positions}")  # Debugging
                for client in self.clients:
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
            print(f"Connection closed with {client_address}")


    def accept_connections(self):
        print("Server started, waiting for clients...")
        while True:
            client_socket, client_address = self.server_socket.accept()
            print(f"Client {client_address} connected")
            self.clients.append(client_socket)
            threading.Thread(target=self.handle_client, args=(client_socket, client_address)).start()


if __name__ == "__main__":
    server = Server('127.0.0.1', 12345)
    server.accept_connections()
