import math

import pygame

class ProjectileBase:
    image = None
    lifetime = 1

    def timestep(self, deltatime, projectiles, zombies):
        self.lifetime -= deltatime

    def render(self, screen):
        pass

    def is_done(self):
        return self.lifetime <= 0

class BulletTrail(ProjectileBase):
    def __init__(self, start, end, color, lifetime=0.1):
        self.start = start
        self.end = end
        self.color = color
        self.lifetime = lifetime

    def render(self, screen, offset):
        pygame.draw.line(screen, self.color, [self.start[0] + offset[0], self.start[1] + offset[1]], [self.end[0] + offset[0], self.end[1] + offset[1]], width=1)
    
class Grenade(ProjectileBase):
    speed = 175

    def __init__(self, start, end, damage):
        self.pos = start
        self.end = end
        self.damage = damage
        
        difference = (end[0] - start[0], end[1] - start[1])
        a = math.sqrt(difference[0] ** 2 + difference[1] ** 2)
        norm_vector = (difference[0] / a, difference[1] / a)

        self.vector = (norm_vector[0] * self.speed, norm_vector[1] * self.speed)

        self.prev_dist = 999999999999

    def timestep(self, deltatime, projectiles, zombies):
        self.pos = (self.pos[0] + self.vector[0] * deltatime, self.pos[1] + self.vector[1] * deltatime)

        dist = math.sqrt((self.end[0] - self.pos[0]) ** 2 + (self.end[1] - self.pos[1]) ** 2)

        # if distance is growing, it means projectile is past it's target. Works even with low framerates
        if (dist > self.prev_dist):
            self.lifetime = -1

            projectiles.append(GrenadeExplosion(self.pos))

            for z in zombies:
                z_pos = z.game_pos()
                dist = math.sqrt((z_pos[0] - self.pos[0]) ** 2 + (z_pos[1] - self.pos[1]) ** 2)

                if dist <= 50:
                    z.hit(self.damage)

        self.prev_dist = dist

    def render(self, screen, offset):
        pygame.draw.circle(screen, (0,0,0), (self.pos[0] + offset[0], self.pos[1] + offset[1]), 5)

class GrenadeExplosion(ProjectileBase):
    max_radius = 60
    speed = 300 # how fast the explosion expands outwards

    def __init__(self, pos):
        self.pos = pos
        self.radius = 1

    def timestep(self, deltatime, projectiles, zombies):
        self.radius += self.speed * deltatime

        if self.radius > self.max_radius:
            self.lifetime = -1

    def render(self, screen, offset):
        pygame.draw.circle(screen, (255,0,0), (self.pos[0] + offset[0], self.pos[1] + offset[1]), self.radius, width=5)