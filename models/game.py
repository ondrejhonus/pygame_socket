import pygame
from models.player import Player
from models.bullet import Bullet
from settings import WINDOW_WIDTH, WINDOW_HEIGHT, FPS

class Game:
    def __init__(self, client, player):
        self.client = client
        self.player = player
        self.running = True
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()

    def run(self):
        print("Game loop started!")

        while self.running:
            self.screen.fill((50, 50, 50))  # BG
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.draw()
            self.bullet_collision()
            
    def draw(self):
        keys = pygame.key.get_pressed()
        self.player.move(keys)
        self.player.shoot(keys)

        # Send position to the server
        self.client.send_position(self.player)

        # Draw local player
        pygame.draw.rect(self.screen, self.player.color, (*self.player.pos, self.player.size, self.player.size))

        # Draw other players (positions + bullets)
        for addr, (pos, color, bullets) in self.client.player_positions.items():
            if addr != self.client.client_socket.getsockname():
                pygame.draw.rect(self.screen, color, (*pos, self.player.size, self.player.size))
            for bullet_pos, bullet_direction in bullets:
                pygame.draw.circle(self.screen, (255, 0, 0), (int(bullet_pos[0]), int(bullet_pos[1])), 5)

        for bullet in self.player.bullets:
            bullet.move()
            # bullet.draw(self.screen)
            
        pygame.display.flip()
        self.clock.tick(FPS)
                
    def bullet_collision(self):
        # Check if bullet is out of bounds
        for bullet in self.player.bullets:
            if bullet.pos[0] < 0 or bullet.pos[0] > WINDOW_WIDTH or bullet.pos[1] < 0 or bullet.pos[1] > WINDOW_HEIGHT:
                print("Bullet out of bounds")
                self.player.bullets.remove(bullet)
                continue

            # Check collision with other players
            for addr, (pos, color, bullets) in self.client.player_positions.items():
                if addr != self.client.client_socket.getsockname():
                    player_rect = pygame.Rect(*pos, self.player.size, self.player.size)
                    bullet_rect = pygame.Rect(bullet.pos[0], bullet.pos[1], 5, 5)
                    if player_rect.colliderect(bullet_rect):
                        print(f"Bullet hit player at {pos}")
                        self.player.bullets.remove(bullet)
                        break