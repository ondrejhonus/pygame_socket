import pygame
import random

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