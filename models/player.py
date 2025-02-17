import pygame
import random
import time
from models.bullet import Bullet

class Player:
    def __init__(self):
        self.size = 50
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.pos = [375, 275]
        self.speed = 5
        self.bullets = [] 
        self.last_shot_time = 0  # Track the last time a bullet was shot

    def move(self, keys):

        if keys[pygame.K_w]:
            self.pos[1] -= self.speed
        if keys[pygame.K_s]:
            self.pos[1] += self.speed
        if keys[pygame.K_a]:
            self.pos[0] -= self.speed
        if keys[pygame.K_d]:
            self.pos[0] += self.speed

    def shoot(self, keys):
        current_time = time.time()
        if keys[pygame.K_SPACE] and current_time - self.last_shot_time >= .5:  # PShoot once per sec
            direction = (1, 0)  # Shoots to the right for now
            bullet = Bullet(self.pos[0] + self.size // 2, self.pos[1] + self.size // 2, direction)
            self.bullets.append(bullet)
            self.last_shot_time = current_time
            print(f"Shooting bullet at {bullet.pos}") 
