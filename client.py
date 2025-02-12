import pygame
import socket
import threading
import pickle
import random
from models.game import Game
from models.player import Player


class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, port))
        self.client_socket.settimeout(2.0)  # Set a timeout for the socket
        self.player_positions = {}

    def send_position(self, player):
        while True:
            data = pickle.dumps((player.pos, player.color))
            self.client_socket.sendall(len(data).to_bytes(4, byteorder='big'))
            self.client_socket.sendall(data)
            pygame.time.wait(1)

    def receive_positions(self):
        while True:
            data_length = self.client_socket.recv(4)
            if not data_length:
                break
            data_length = int.from_bytes(data_length, byteorder='big')
            
            data = b""
            try:
                chunk = self.client_socket.recv(data_length - len(data))
            except socket.timeout:
                print("Socket timeout, retrying...")
                continue
            chunk = self.client_socket.recv(data_length - len(data))
            if not chunk:
                break
            data += chunk
            
            try:
                self.player_positions = pickle.loads(data)
            except pickle.UnpicklingError:
                pass

        pygame.quit()
        self.client.client_socket.close()

if __name__ == "__main__":
    client = Client('127.0.0.1', 12345)
    player = Player()
    game = Game(client, player)
    game.run()