import pygame

class Bullet:
    def __init__(self, x, y, direction):
        self.pos = [x, y]
        self.speed = 10
        self.direction = direction  # Direction should be a tuple (dx, dy)
        self.size = 5
        self.color = (255, 0, 0)

    def move(self):
        self.pos[0] += self.direction[0] * self.speed
        self.pos[1] += self.direction[1] * self.speed

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.pos[0]), int(self.pos[1])), self.size)
