import json

import pygame

import game.load as load
import game.utils as utils
from game.map import Road, Start, SCALE


class ZombieBase:
    image = None
    speed = 1
    
    def __init__(self, tile):
        self.x, self.y = tile.x, tile.y
        self.tile = tile
    
    def timestep(self, deltatime):
        if (type(self.tile) in (Road, Start)):
            dest = self.tile.next
            thresh = 0.01
            if (abs(self.x - dest.x) < thresh and abs(self.y - dest.y) < thresh):
                self.tile = self.tile.next
            if type(self.tile) not in (Road, Start):
                self.tile = None
                return
            dist = ((dest.x - self.x)**2 + (dest.y - self.y)**2)**0.5
            if (dist <= 0): return
            self.x += (dest.x - self.x)/dist * self.speed * deltatime
            self.y += (dest.y - self.y)/dist * self.speed * deltatime
    
    def render(self, screen, off = [0,0]):
        off = [
            off[0] + (SCALE - self.image.get_width())//2,
            off[1] + (SCALE - self.image.get_height())//2
        ]
        screen.blit(self.image, (self.x*SCALE + off[0], self.y*SCALE + off[1]))


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
    
