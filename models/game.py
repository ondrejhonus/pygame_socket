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
        pygame.font.init()

    def run(self):
        print("Game loop started!")

        while self.running:
            self.screen.fill((50, 50, 50))  # BG
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.draw()
            self.bullet_collision()
        else:
            self.game_lost()
            
    def draw(self):
        keys = pygame.key.get_pressed()
        self.player.move(keys)
        self.player.shoot(keys)
        self.client.send_position(self.player)

        font = pygame.font.Font(None, 24)

        pygame.draw.rect(self.screen, self.player.color, (*self.player.pos, self.player.size, self.player.size))
        hp_text = font.render(f"{self.player.hp} HP", True, (255, 255, 255))
        self.screen.blit(hp_text, (self.player.pos[0], self.player.pos[1] - 20))
        # print(self.client.player_positions)
        for addr, (pos, color, bullets, hp) in self.client.player_positions.items():
            if addr != self.client.client_socket.getsockname():
                pygame.draw.rect(self.screen, color, (*pos, self.player.size, self.player.size))
                hp_text = font.render(f"{hp} HP", True, (255, 255, 255))
                self.screen.blit(hp_text, (pos[0], pos[1] - 20))


            for bullet_pos, bullet_direction in bullets:
                pygame.draw.circle(self.screen, (255, 0, 0), (int(bullet_pos[0]), int(bullet_pos[1])), 5)

        for bullet in self.player.bullets:
            bullet.move()
        
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
            for addr, (pos, color, bullets, hp) in self.client.player_positions.items():
                if addr != self.client.client_socket.getsockname():
                    player_rect = pygame.Rect(*pos, self.player.size, self.player.size)
                    bullet_rect = pygame.Rect(bullet.pos[0], bullet.pos[1], 5, 5)
                    if player_rect.colliderect(bullet_rect):
                        print(f"Bullet hit player at {pos}")
                        self.client.send_damage(addr, 10)
                        self.player.bullets.remove(bullet)
                        self.game_won()
                        break
    def game_won(self):
        print("Game over!")
        self.screen.fill((0, 0, 0))
        font = pygame.font.Font(None, 74)
        game_over_text = font.render("YOU WON", True, (0, 255, 0))
        text_rect = game_over_text.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        self.screen.blit(game_over_text, text_rect)
        pygame.display.flip()
        pygame.time.wait(3000)
        self.running = False
        pygame.quit()
        quit()
    
    def game_lost(self):
        print("Game over!")
        self.running = False
        self.screen.fill((0, 0, 0))
        font = pygame.font.Font(None, 74)
        game_over_text = font.render("YOU LOST", True, (255, 0, 0))
        text_rect = game_over_text.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        self.screen.blit(game_over_text, text_rect)
        pygame.display.flip()
        pygame.time.wait(3000)
        pygame.quit()
        quit()