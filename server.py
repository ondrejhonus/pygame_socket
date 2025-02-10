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

                player_pos = pickle.loads(data)
                self.player_positions[client_address] = player_pos

                players_data = pickle.dumps(self.player_positions)
                for client in self.clients:
                    client.sendall(len(players_data).to_bytes(4, byteorder='big'))
                    client.sendall(players_data)
        except Exception as e:
            print(f"Error with client {client_address}: {e}")
        finally:
            client_socket.close()
            self.clients.remove(client_socket)
            del self.player_positions[client_address]
            print(f"Connection closed with {client_address}")

    def accept_connections(self):
        print("Server started, waiting for clients...")
        while True:
            client_socket, client_address = self.server_socket.accept()
            self.clients.append(client_socket)
            threading.Thread(target=self.handle_client, args=(client_socket, client_address)).start()

if __name__ == "__main__":
    server = Server('127.0.0.1', 12345)
    server.accept_connections()
