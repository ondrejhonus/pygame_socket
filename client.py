import socket
import threading
import pickle
from models.game import Game
from models.player import Player
from time import sleep

class Client:
    def __init__(self, host, port):
        print(f"Connecting to server {host}:{port}...")
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, port))
        self.client_socket.settimeout(5.0)  # Set a timeout for the socket
        self.player_positions = {}
        print("Connected!")

        self.receive_thread = threading.Thread(target=self.receive_positions, daemon=True)
        self.receive_thread.start()

    def send_position(self, player):
        try:
            data = pickle.dumps((player.pos, player.color, [(b.pos, b.direction) for b in player.bullets]))
            self.client_socket.sendall(len(data).to_bytes(4, byteorder='big'))
            self.client_socket.sendall(data)
            sleep(0.01) 
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

                # Check is data is not corrupted before accepting
                if len(data) != data_length:
                    print(f"Data size mismatch. Expected {data_length}, got {len(data)}")
                    continue

                # Unpickle the received data
                try:
                    received_data = pickle.loads(data)
                    if isinstance(received_data, dict):
                        self.player_positions = received_data
                        # print(f"Received positions: {self.player_positions}")
                    else:
                        print("Received data is not a dictionary.")
                except pickle.UnpicklingError as e:
                    print(f"Failed to unpickle data: {e}")
                    continue

            except Exception as e:
                print(f"Failed to receive positions: {e}")
                break


if __name__ == "__main__":
    print("Starting client...")
    client = Client('127.0.0.1', 12345)
    player = Player()
    game = Game(client, player)
    print("Running game loop...")
    game.run()
