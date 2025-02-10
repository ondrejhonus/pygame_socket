import pygame
import socket
import threading
import pickle
import random

# Client settings
host = '127.0.0.1'
port = 12345
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((host, port))
client_socket.settimeout(2.0)  # Set a timeout for the socket

# Pygame settings
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Pygame Socket Client")
clock = pygame.time.Clock()

# Player settings
player_size = 50
player_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
player_pos = [375, 275]
player_speed = 5

# Dictionary to store all player positions and colors
player_positions = {}

def send_position():
    while True:
        data = pickle.dumps((player_pos, player_color))
        client_socket.sendall(len(data).to_bytes(4, byteorder='big'))
        client_socket.sendall(data)
        pygame.time.wait(1)

def receive_positions():
    global player_positions
    while True:
        data_length = client_socket.recv(4)
        if not data_length:
            break
        data_length = int.from_bytes(data_length, byteorder='big')
        
        data = b""
        try:
            chunk = client_socket.recv(data_length - len(data))
        except socket.timeout:
            print("Socket timeout, retrying...")
            continue
        chunk = client_socket.recv(data_length - len(data))
        if not chunk:
            break
        data += chunk
        
        try:
            player_positions = pickle.loads(data)
        except pickle.UnpicklingError:
            pass

# Start threads for sending and receiving data
threading.Thread(target=send_position, daemon=True).start()
threading.Thread(target=receive_positions, daemon=True).start()

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        player_pos[1] -= player_speed
    if keys[pygame.K_s]:
        player_pos[1] += player_speed
    if keys[pygame.K_a]:
        player_pos[0] -= player_speed
    if keys[pygame.K_d]:
        player_pos[0] += player_speed

    screen.fill((0, 0, 0))
    for pos, color in player_positions.values():
        pygame.draw.rect(screen, color, (*pos, player_size, player_size))
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
client_socket.close()