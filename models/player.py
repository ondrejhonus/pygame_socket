import pygame
import random
from models.bullet import Bullet

class Player:
    def __init__(self):
        self.size = 50
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.pos = [375, 275]
        self.speed = 5
        self.bullets = []  # Track bullets

    def move(self, keys):
        # print(f"Keys pressed: {keys}")  # Debugging

        if keys[pygame.K_w]:
            self.pos[1] -= self.speed
            print("Moving up")  # Debugging
        if keys[pygame.K_s]:
            self.pos[1] += self.speed
            print("Moving down")  # Debugging
        if keys[pygame.K_a]:
            self.pos[0] -= self.speed
            print("Moving left")  # Debugging
        if keys[pygame.K_d]:
            self.pos[0] += self.speed
            print("Moving right")  # Debugging


    def shoot(self, keys):
        if keys[pygame.K_SPACE]:  # Press space to shoot
            direction = (1, 0)  # Shoots to the right for now
            bullet = Bullet(self.pos[0] + self.size // 2, self.pos[1] + self.size // 2, direction)
            self.bullets.append(bullet)
            print(f"Shooting bullet at {bullet.pos}")  # Debugging
