import socket
import threading
import pickle
from models.game import Game
from models.player import Player
import pygame

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

class Client:
    def __init__(self, host, port, game):
        print(f"Connecting to server {host}:{port}...")
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, port))
        self.client_socket.settimeout(10.0)  # Set a timeout for the socket
        self.player_positions = {}
        self.game = game
        print("Connected!")
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.running = True

        self.receive_thread = threading.Thread(target=self.receive_positions, daemon=True)
        self.receive_thread.start()

    def send_position(self, player):
        try:
            data = pickle.dumps((player.pos, player.color, [(b.pos, b.direction) for b in player.bullets], player.hp))
            self.client_socket.sendall(len(data).to_bytes(4, byteorder='big'))
            self.client_socket.sendall(data)
        except Exception as e:
            print(f"Failed to send position: {e}")

    def receive_positions(self):
        while True:
            try:
                # Read the 4-byte length header
                data_length_bytes = self.client_socket.recv(4)
                if not data_length_bytes:
                    print("Connection closed by server.")
                    break

                data_length = int.from_bytes(data_length_bytes, byteorder='big')
                if data_length == 0:
                    print("Received empty data, skipping.")
                    continue

                # Read the actual data
                data = b""
                while len(data) < data_length:
                    chunk = self.client_socket.recv(data_length - len(data))
                    if not chunk:
                        print("Incomplete data received.")
                        break
                    data += chunk

                # Check if data is not corrupted before accepting
                if len(data) != data_length:
                    print(f"Data size mismatch. Expected {data_length}, got {len(data)}")
                    continue

                # Unpickle the received data
                try:
                    received_data = pickle.loads(data)
                    if isinstance(received_data, dict):
                        self.player_positions = received_data
                        for addr, (_, _, _, hp) in self.player_positions.items():
                            if addr == self.client_socket.getsockname():
                                player.hp = hp
                                game.player.hp = hp
                                if hp < 100:
                                    game.running = False
                    else:
                        print("Received data is not a dictionary.")
                except pickle.UnpicklingError as e:
                    print(f"Failed to unpickle data: {e}")
                    continue

            except Exception as e:
                print(f"Failed to receive positions: {e}")
                break

    def send_damage(self, addr, damage):
        try:
            message = {'action': 'damage', 'addr': addr, 'damage': damage}
            data = pickle.dumps(message)
            data_length = len(data).to_bytes(4, byteorder='big')
            self.client_socket.sendall(data_length + data)
        except Exception as e:
            print(f"Error sending damage to server: {e}")

if __name__ == "__main__":
    host = input("Enter the server IP address (default: localhost): ") or "localhost"
    player = Player()
    game = Game(None, player)
    client = Client(host, 12345, game)
    game.client = client
    print("Running game loop...")
    game.run()