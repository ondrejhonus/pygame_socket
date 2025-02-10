import pygame
import socket
import threading
import pickle
import random

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

class Player:
    def __init__(self):
        self.size = 50
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.pos = [375, 275]
        self.speed = 5

    def move(self, keys):
        if keys[pygame.K_w]:
            self.pos[1] -= self.speed
        if keys[pygame.K_s]:
            self.pos[1] += self.speed
        if keys[pygame.K_a]:
            self.pos[0] -= self.speed
        if keys[pygame.K_d]:
            self.pos[0] += self.speed

class Game:
    def __init__(self, client, player):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Pygame Socket Client")
        self.clock = pygame.time.Clock()
        self.client = client
        self.player = player
        self.running = True

    def run(self):
        threading.Thread(target=self.client.send_position, args=(self.player,), daemon=True).start()
        threading.Thread(target=self.client.receive_positions, daemon=True).start()

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            keys = pygame.key.get_pressed()
            self.player.move(keys)

            self.screen.fill((0, 0, 0))
            for pos, color in self.client.player_positions.values():
                pygame.draw.rect(self.screen, color, (*pos, self.player.size, self.player.size))
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        self.client.client_socket.close()

if __name__ == "__main__":
    client = Client('127.0.0.1', 12345)
    player = Player()
    game = Game(client, player)
    game.run()