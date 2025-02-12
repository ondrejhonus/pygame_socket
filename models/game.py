import pygame
import threading


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