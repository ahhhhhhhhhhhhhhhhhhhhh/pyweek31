import random
import json

import pygame

import game.load as load
import game.utils as utils
from game.map import Road, Start, SCALE


class ZombieBase:
    image = None
    speed = 1
    max_health = 100
    
    def __init__(self, tile):
        self.x, self.y = tile.x, tile.y
        self.tile = tile
        self.goal = random.choice(list(self.tile.next.keys()))
        self.dest = self.tile.next[self.goal][0]
        self.last_render_pos = []

        self.health = self.max_health

        self.max_health_bar_width = 35
        self.update_health_bar()
    
    def timestep(self, deltatime):
        if (type(self.tile) in (Road, Start)):
            thresh = 0.01
            if (abs(self.x - self.dest.x) < thresh and abs(self.y - self.dest.y) < thresh):
                self.tile = self.dest
                if type(self.tile) not in (Road, Start):
                    self.tile = None
                    return
                self.dest = self.tile.next[self.goal][0]
            dist = ((self.dest.x - self.x)**2 + (self.dest.y - self.y)**2)**0.5
            if (dist <= 0): return
            self.x += (self.dest.x - self.x)/dist * self.speed * deltatime
            self.y += (self.dest.y - self.y)/dist * self.speed * deltatime
    
    def render(self, screen, off = [0,0]):
        off = [
            off[0] + (SCALE - self.image.get_width())//2,
            off[1] + (SCALE - self.image.get_height())//2
        ]
        self.last_render_pos = (self.x*SCALE + off[0], self.y*SCALE + off[1])
        screen.blit(self.image, self.last_render_pos)

        self.update_health_bar()
        center = self.center_pos()
        screen.blit(self.health_bar, [center[0] - self.health_bar.get_width() // 2, center[1] - 25])
    
    def render_pos(self):
        return self.last_render_pos

    def center_pos(self):
        return [self.last_render_pos[0] + self.image.get_width() / 2, self.last_render_pos[1] + self.image.get_height() / 2]
    
    def dist(self):
        return self.tile.next[self.goal][1]

    def hit(self, damage):
        self.health -= damage

    def is_dead(self):
        return self.health <= 0

    def update_health_bar(self):
        self.health_bar = pygame.Surface((self.max_health_bar_width * (self.health / self.max_health), 5))
        self.health_bar.fill((0, 255, 0))

class Zombie(ZombieBase):
    image = load.image("smallzombie.png")
    speed = 1


class FastZombie(ZombieBase):
    image = load.image("smallzombie.png")
    speed = 2


class Waves:
    zombiemap = {"zombie": Zombie,
                 "fastzombie": FastZombie}

    def __init__(self, filepath):
        filepath = load.handle_path(filepath)

        with open(filepath, "r") as file:
            lines = file.readlines()

        lines = [json.loads(line) for line in lines]
        waves = []
    
        for i, line in enumerate(lines):
            waves.append([])
            for j in range(len(line)):
                waves[i].append({})
                for key in lines[i][j]:
                    waves[i][j][Waves.zombiemap[key]] = lines[i][j][key]

        print(waves)

class ProjectileBase:
    image = None
    lifetime = 1 

    def timestep(self, deltatime):
        self.lifetime -= deltatime

    def render(self, screen):
        pass

    def is_done(self):
        return self.lifetime <= 0

class BulletTrail(ProjectileBase):
    lifetime = 0.1

    def __init__(self, start, end, color):
        self.start = start
        self.end = end
        self.color = color

    def render(self, screen):
        pygame.draw.line(screen, self.color, self.start, self.end, width=1)
    