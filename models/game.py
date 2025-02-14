import pygame
from models.player import Player
from models.bullet import Bullet


class Game:
    def __init__(self, client, player):
        self.client = client
        self.player = player
        self.running = True
        self.screen = pygame.display.set_mode((800, 600))
        self.clock = pygame.time.Clock()

    def run(self):
        print("Game loop started!")

        while self.running:
            self.screen.fill((50, 50, 50))  # Background color

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            keys = pygame.key.get_pressed()  # Get keys here
            self.player.move(keys)  # Move player
            self.player.shoot(keys)  # Handle shooting

            # Send position to the server
            self.client.send_position(self.player)

            # Draw the local player
            pygame.draw.rect(self.screen, self.player.color, (*self.player.pos, self.player.size, self.player.size))

            # Draw other players (positions + bullets)
            for addr, (pos, color, bullets) in self.client.player_positions.items():
                if addr != self.client.client_socket.getsockname():
                    pygame.draw.rect(self.screen, color, (*pos, self.player.size, self.player.size))
                for bullet_pos, bullet_direction in bullets:
                    pygame.draw.circle(self.screen, (255, 0, 0), (int(bullet_pos[0]), int(bullet_pos[1])), 5)

            # Update bullets
            for bullet in self.player.bullets:
                bullet.move()
                bullet.draw(self.screen)
            
            pygame.display.flip()
            self.clock.tick(60)


