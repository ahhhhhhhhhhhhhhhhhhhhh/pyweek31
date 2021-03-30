import random

import game.load as load
import game.utils as utils

from game.map import Road, Start, SCALE

import pygame

class ZombieBase:
    image = None
    speed = 1
    
    def __init__(self, tile):
        self.x, self.y = tile.x, tile.y
        self.tile = tile
        self.goal = random.choice(list(self.tile.next.keys()))
        self.dest = self.tile.next[self.goal]
    
    def timestep(self, deltatime):
        if (type(self.tile) in (Road, Start)):
            thresh = 0.01
            if (abs(self.x - self.dest.x) < thresh and abs(self.y - self.dest.y) < thresh):
                self.tile = self.dest
                if type(self.tile) not in (Road, Start):
                    self.tile = None
                    return
                self.dest = self.tile.next[self.goal]
            dist = ((self.dest.x - self.x)**2 + (self.dest.y - self.y)**2)**0.5
            if (dist <= 0): return
            self.x += (self.dest.x - self.x)/dist * self.speed * deltatime
            self.y += (self.dest.y - self.y)/dist * self.speed * deltatime
    
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

    
