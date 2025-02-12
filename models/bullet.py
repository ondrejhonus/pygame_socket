import pygame

class Bullet:
    def __init__(self, pos, direction):
        self.pos = pos
        self.direction = direction
        self.speed = 10
        self.size = 10

    def move(self):
        self.pos[0] += self.direction[0] * self.speed
        self.pos[1] += self.direction[1] * self.speed

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 255, 255), self.pos, self.size)