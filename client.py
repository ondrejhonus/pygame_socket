import pygame
import socket
import threading
import pickle
import random
from models.game import Game
from models.player import Player

class Client:
    def __init__(self, host, port):
        print(f"Connecting to server {host}:{port}...")
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, port))
        self.client_socket.settimeout(2.0)  # Set a timeout for the socket
        self.player_positions = {}
        print("Connected!")

        # Start the receive_positions method in a separate thread
        self.receive_thread = threading.Thread(target=self.receive_positions)
        self.receive_thread.daemon = True
        self.receive_thread.start()

    def send_position(self, player):
        try:
            data = pickle.dumps((player.pos, player.color, [(b.pos, b.direction) for b in player.bullets]))
            self.client_socket.sendall(len(data).to_bytes(4, byteorder='big'))
            self.client_socket.sendall(data)
        except Exception as e:
            print(f"Failed to send position: {e}")

    def receive_positions(self):
        while True:
            try:
                data_length = self.client_socket.recv(4)
                if not data_length:
                    print("No data received!")  # Debugging
                    break
                data_length = int.from_bytes(data_length, byteorder='big')

                data = b""
                while len(data) < data_length:
                    chunk = self.client_socket.recv(data_length - len(data))
                    if not chunk:
                        print("Chunk not received!")  # Debugging
                        break
                    data += chunk

                if data:
                    self.player_positions = pickle.loads(data)
                    print(f"Received positions: {self.player_positions}")  # Debugging
            except socket.timeout:
                print("Socket timeout, retrying...")
                continue


if __name__ == "__main__":
    print("Starting client...")
    client = Client('127.0.0.1', 12345)
    player = Player()
    game = Game(client, player)
    print("Running game loop...")
    game.run()
