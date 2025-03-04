import socket
import threading
import pickle
import time
from settings import SERVER_PORT

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

                # Receive full uncorrupted data
                data = b""
                while len(data) < data_length:
                    chunk = client_socket.recv(data_length - len(data))
                    if not chunk:
                        print("Connection lost while receiving data.")
                        return
                    data += chunk

                # Unpickle the received data
                try:
                    message = pickle.loads(data)
                    if isinstance(message, dict) and message.get('action') == 'damage':
                        self.apply_damage(message['addr'], message['damage'])
                    else:
                        pos, color, bullets, hp = message  # Extract HP from data
                        self.player_positions[client_address] = (pos, color, bullets, hp)
                        print(f"Updated player position for {client_address}: {self.player_positions[client_address]}")
                except Exception as e:
                    print(f"Failed to unpickle data from {client_address}: {e}")
                    continue

                # Broadcast updated data
                players_data = pickle.dumps(self.player_positions)
                for client in self.clients:
                    if client != client_socket:
                        try:
                            client.sendall(len(players_data).to_bytes(4, byteorder='big'))
                            client.sendall(players_data)
                        except Exception as e:
                            print(f"Failed to send data to {client}: {e}")

                # time.sleep(0.1)  # delay game, decrease fps basically

        except (ConnectionResetError, EOFError):
            print(f"Client {client_address} disconnected.")
        finally:
            client_socket.close()
            if client_socket in self.clients:
                self.clients.remove(client_socket)
            self.player_positions.pop(client_address, None)

    def apply_damage(self, addr, damage):
        if addr in self.player_positions:
            pos, color, bullets, hp = self.player_positions[addr]
            hp -= damage
            # hp cant be negative
            hp = max(hp, 0)
            
            self.player_positions[addr] = (pos, color, bullets, hp)
            print(f"Applied {damage} damage to {addr}. New HP: {hp}")
            
            players_data = pickle.dumps(self.player_positions)
            for client in self.clients:
                try:
                    client.sendall(len(players_data).to_bytes(4, byteorder='big'))
                    client.sendall(players_data)
                except Exception as e:
                    print(f"Failed to send data to {client}: {e}")

    def accept_connections(self):
        while True:
            client_socket, client_address = self.server_socket.accept()
            print(f"Client {client_address} connected")
            self.clients.append(client_socket)
            threading.Thread(target=self.handle_client, args=(client_socket, client_address), daemon=True).start()

if __name__ == "__main__":
    server_ip = input("Enter server IP (default: localhost): ")
    if server_ip == "":
        server_ip = "localhost"
    server = Server(server_ip, SERVER_PORT)
    server.accept_connections()