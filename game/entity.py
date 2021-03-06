import random
import json

import pygame

import game.load as load
from game.sound import SoundEffectsManager
from game.map import Road, Start, SCALE

class ZombieBase:
    image = None
    speed = 1
    max_health = 200
    reward = 20
    healthbar_off_y = 20
    lives_impact = 1
    
    def __init__(self, game, tile):
        self.game = game
        self.x, self.y = tile.x, tile.y
        self.tile = tile
        self.goal = random.choice(list(self.tile.next.keys()))
        self.dest = self.tile.next[self.goal][0]
        self.last_render_pos = [0,0]

        self.health = self.max_health

        self.max_health_bar_width = 30
        self.update_health_bar()

        self.stun_timer = 0
        self.disp_offset = [random.random()/2-0.25, random.random()/2-0.25]
    
    def timestep(self, deltatime):
        if self.stun_timer > 0:
            self.stun_timer -= deltatime
            return

        if (type(self.tile) in (Road, Start)):
            thresh = deltatime * self.speed
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
            off[1] + (SCALE - self.image.get_height()) - SCALE//3
        ]
        tpos = [
            self.x + self.disp_offset[0],
            self.y + self.disp_offset[1]
        ]
        self.last_render_pos = (tpos[0]*SCALE + off[0], tpos[1]*SCALE + off[1])
        screen.blit(self.image, self.last_render_pos)

        self.update_health_bar()
        center = self.center_pos()

        if self.health < self.max_health:
            screen.blit(self.health_bar, [center[0] - self.health_bar.get_width() // 2, center[1] - self.healthbar_off_y])
    
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
        self.health_bar = pygame.Surface((self.max_health_bar_width * (self.health / self.max_health), 3))
        self.health_bar.fill((0, 255, 0))

    def stun(self, duration):
        self.stun_timer = duration

class Zombie(ZombieBase):
    image = load.image("smallzombie.png")
    speed = 1

class FastZombie(ZombieBase):
    image = load.image("fastzombie.png")
    speed = 1.75
    reward = 25

class GiantZombie(ZombieBase):
    image = load.image("buffzombie.png")
    speed = 0.6
    max_health = 2000
    reward = 100
    healthbar_off_y = 40
    lives_impact = 5

class BabyZombie(ZombieBase):
    image = load.image("babyzombie.png")
    speed = 2.5
    max_health = 100
    reward = 30

class ShieldZombie(ZombieBase):
    image = load.image("smallzombie.png")
    shieldimage = load.image("shield.png")
    speed = 1
    max_health = 300
    reward = 30
    shield_health = 50
    
    def __init__(self, game, tile):
        super().__init__(game, tile)
        self.shield = self.shield_health
        
    
    def hit(self, damage):
        if self.shield > 0:
            self.shield -= damage
        else:
            self.health -= damage
    
    def render(self, screen, off = [0,0]):
        super().render(screen, off)
        if self.shield > 0:
            screen.blit(self.shieldimage, [
                self.last_render_pos[0] + self.image.get_width()//3,
                self.last_render_pos[1] + self.image.get_height()//3
            ])


class SummonerZombie(ZombieBase):
    image = load.image("smartzombie.png")
    max_health = 500
    speed = 0.5
    spawn_rate = 5 # time between spawns
    spawn_group = 3
    reward = 150
    spawntype = Zombie
    lives_impact = 10
    
    def __init__(self, game, tile):
        super().__init__(game, tile)
        self.last_spawn = self.spawn_rate
        self.spawns = self.spawn_group
    
    def timestep(self, deltatime):
        if self.last_spawn > 0:
            self.last_spawn -= deltatime
            if self.last_spawn > 0.5 and self.spawn_rate - self.last_spawn > 0.5:
                super().timestep(deltatime)
        else:
            zomb = self.spawntype(self.game, self.tile)
            zomb.x = self.x
            zomb.y = self.y
            self.game.zombies.append(zomb)
            self.spawns -= 1
            if self.spawns > 0:
                self.last_spawn = 0.1
            else:
                self.spawns = self.spawn_group
                self.last_spawn = self.spawn_rate


class CarryZombie(ZombieBase):
    image = load.image("cart.png")
    max_health = 1000
    speed = 0.65
    reward = 50
    spawntype = BabyZombie
    spawn_group = 5
    lives_impact = 5
    
    def hit(self, damage):
        if self.health > 0 and self.health < damage:
            for i in range(self.spawn_group):
                zomb = self.spawntype(self.game, self.tile)
                zomb.x = self.x
                zomb.y = self.y
                self.game.zombies.append(zomb)
        super().hit(damage)


class Waves:
    zombiemap = {"zombie": Zombie,
                 "fast": FastZombie,
                 "giant": GiantZombie,
                 "baby": BabyZombie,
                 "shield": ShieldZombie,
                 "summoner": SummonerZombie,
                 "carry": CarryZombie}

    def __init__(self, game, filepath, tmap):
        self.game = game
        filepath = load.handle_path(filepath)

        with open(filepath, "r") as file:
            lines = file.readlines()

        lines = [json.loads(line) for line in lines]
        waves = []
    
        for wave in lines:
            waves.append([])
            for spawnwave in wave:
                waves[-1].append([])
                for i in range(0, len(spawnwave), 2):
                    for _ in range(spawnwave[i+1]):
                        waves[-1][-1].append(Waves.zombiemap[spawnwave[i]])
                    
        self.waves = waves
        for i, spawnwave in enumerate(waves):
            if len(spawnwave) > len(tmap.starts):
                print("WARNING: This wave file has too many spawnpoints on wave " + str(i+1))
        
        self.zombies_to_spawn = [[] for _ in range(len(tmap.starts))]
        self.spawn_timers = [0 for _ in range(len(self.zombies_to_spawn))]
        self.spawn_last = [type(None) for _ in range(len(self.zombies_to_spawn))]
        self.time_threshold = 1
        self.total_waves = len(waves)
        self.current_wave = 0

    def get_next(self):
        if self.waves:
            self.current_wave += 1
            return self.waves.pop(0)
        return False

    def get_finished(self):
        return not self.waves and not any([bool(x) for x in self.zombies_to_spawn])

    def call_next(self, tmap):
        wave = self.get_next()
        self.spawn_last = [type(None) for _ in range(len(self.zombies_to_spawn))]

        if wave:
            for i in range(len(wave)):
                spawnwave = wave[i]
                for ztype in spawnwave:
                    self.zombies_to_spawn[i].append(ztype(self.game, tmap.starts[i]))

    def update(self, zombielist):
        for i in range(len(self.spawn_timers)):
            self.spawn_timers[i] += Waves.loop.get_ticktime()

            if self.zombies_to_spawn[i]:
                normal = self.spawn_timers[i] > self.time_threshold
                micro_wave = self.spawn_timers[i] > self.time_threshold / 2
                micro_wave = micro_wave and isinstance(self.zombies_to_spawn[i][0], self.spawn_last[i])

                if normal or micro_wave:
                    self.spawn_timers[i] = 0
                    zombielist.append(self.zombies_to_spawn[i].pop(0))
                    self.spawn_last[i] = type(zombielist[i])

    def get_progress(self): # returns (current_wave, total_waves)
        return self.current_wave, self.total_waves

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
    def __init__(self, start, end, color, lifetime=0.1):
        self.start = start
        self.end = end
        self.color = color
        self.lifetime = lifetime

    def render(self, screen, offset):
        pygame.draw.line(screen, self.color, [self.start[0] + offset[0], self.start[1] + offset[1]], [self.end[0] + offset[0], self.end[1] + offset[1]], width=1)
    
