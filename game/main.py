from abc import ABC
import math
import random

import pygame

import game.load as load
from game.map import TileMap, Start, Road, ready_tiles, Tower
from game.utils import Text, Button
from game.sound import SoundManager
import game.entity as entity

class Loop:
    def __init__(self, screen, scene, scenedict, soundManager):
        self.soundManager = soundManager
        self.scene = scene
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.scenedict = scenedict
        self.events = []
        self.requested_cursor = None
        self.ticktime = 0
        self.fps_text = Text("", [10,10], color=(0,0,0))

    def start(self):
        while True:
            self.events.clear()
            self.requested_cursor = None
            for event in pygame.event.get():
                if (event.type == pygame.QUIT
                or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE)):
                    self.end_game()
                self.events.append(event)

            self.screen.fill((0,128,0))

            # this is where the magic happens
            self.scene.update(self)
            self.soundManager.update(self)

            self.handle_cursor()
            self.fps_text.update_text(str(round(self.clock.get_fps())))
            self.fps_text.draw(self.screen)
            
            pygame.display.flip()
            self.ticktime = self.clock.tick(144) / 1000
            self.ticktime = min(self.ticktime, 0.1)

    def switch_scene(self, new_scene):
        # new_scene is a Scene subclass or a string key
        if isinstance(new_scene, Scene):
            self.scene = new_scene
        else:
            self.scene = self.scenedict[new_scene]

    def end_game(self):
        pygame.quit()
        raise SystemExit

    def get_events(self):
        return self.events

    def request_cursor(self, cursor):
        self.requested_cursor = cursor

    def handle_cursor(self):
        if self.requested_cursor:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def get_ticktime(self):
        return self.ticktime

            
class Scene(ABC):
    def __init__(self, screen):
        self.screen = screen

    def update(self, loop):
        pass


class Game(Scene):
    def __init__(self, screen):
        self.id = "game"
        self.screen = screen
        
        self.tmap = TileMap(load.image("maps/map1_bg.png"), load.image("maps/map1_blocking.png"))
        self.waves = entity.Waves("maps/map1_waves.txt")

        self.tmap_offset = [60,60]
        self.zombies = []
        self.zombies.append(entity.Zombie(random.choice(self.tmap.starts)))

        self.lives = 50
        self.display_lives = Text("", [1100, 20], size=32)

        self.towers = []
    
    def update(self, loop):
        deltatime = loop.get_ticktime()
        
        # spawning zombies
        if random.randint(0,100) == 0:
            self.zombies.append(entity.Zombie(random.choice(self.tmap.starts)))
        self.tmap.render(self.screen, self.tmap_offset)

        # updating lives text
        self.display_lives.update_text("Lives: " + str(self.lives))
        self.display_lives.draw(self.screen)

        # building towers
        selected_tile = self.tmap.screen_to_tile_coords(pygame.mouse.get_pos())
        if selected_tile:
            coords = self.tmap.tile_to_screen_coords(selected_tile)
            canbuild = self.tmap.can_build(selected_tile)

            if canbuild:
                self.screen.blit(self.tmap.selector_open, coords)
            else:
                self.screen.blit(self.tmap.selector_closed, coords)
            
            for event in TileMap.loop.get_events():
                if event.type == pygame.MOUSEBUTTONDOWN and not getattr(event, "used", False) and event.button == 1:
                    event.used = True
                    
                    if canbuild:
                        print("building tower", selected_tile)
                        new_tower = Tower(coords[0], coords[1])
                        self.tmap.blocking[selected_tile[0]][selected_tile[1]] = new_tower
                        self.towers.append(new_tower)

        # updating zombies and deleting zombies that reach end
        to_del = []
        for zombie in self.zombies:
            zombie.timestep(deltatime)
            zombie.render(self.screen, self.tmap_offset)
            if zombie.tile == None:
                to_del.append(zombie)
                self.lives -= 1
        for zombie in to_del:
            self.zombies.remove(zombie)

        # updating towers
        for tower in self.towers:
            tower_pos = tower.center_pos()
            pygame.draw.circle(self.screen, (255,255,255), tower_pos, tower.max_range, width=1)
            

            if not tower.update(deltatime):
                continue

            in_range = []
            for z in self.zombies:
                z_pos = z.center_pos()
                dist = math.sqrt((z_pos[0] - tower_pos[0]) ** 2 + (z_pos[1] - tower_pos[1]) ** 2)
                if dist <= tower.max_range:
                    in_range.append(z)

            if len(in_range) == 0:
                continue

            # targets zombie closest to end
            target = min(in_range, key=lambda z: z.dist())

            pygame.draw.line(self.screen, (255,255,255), tower_pos, target.center_pos())
            tower.fire()
            target.hit(tower.damage)
            if target.is_dead():
                self.zombies.remove(target)
            
        
            
class MainMenu(Scene):
    def __init__(self, screen):
        self.id = "menu"
        self.screen = screen
        self.t = Text("John Brawn", [840, 40], 64, centered=True)
        self.b = Button("[Play if you dare...]", [840, 130], 32, centered=True)
        self.b.washovered = False
        self.sb = Button("Settings", [840, 190], 32, centered=True)
        self.sb.washovered = False

        self.zombie = load.image("zombie.png").convert_alpha()
        self.officer = load.image("officer.png").convert_alpha()
        self.house = load.image("house.png").convert_alpha()
        self.i = 0

    def update(self, loop):
        self.i += 1.5 * loop.get_ticktime()
        rotated = pygame.transform.rotate(self.zombie, math.sin(self.i) * 10)
        self.screen.blit(self.house, [-240,-270])
        self.screen.blit(self.officer, self.officer.get_rect(center=(300,500)))
        self.screen.blit(rotated, rotated.get_rect(center=(980,500)))

        self.t.draw(self.screen)
        self.b.draw(self.screen)
        self.sb.draw(self.screen)

        if self.b.clicked:
            loop.switch_scene("game")

        if self.b.hovered:
            self.b.update_color((128,255,0))
            self.b.washovered = True
        elif self.b.washovered:
            self.b.update_color((255,255,255))
        
        if self.sb.clicked:
            loop.switch_scene("settings")

        if self.sb.hovered:
            self.sb.update_color((128,255,0))
            self.sb.washovered = True
        elif self.sb.washovered:
            self.sb.update_color((255,255,255))

class Settings(Scene):
    def __init__(self, screen):
        self.id = "settings"
        self.screen = screen
        self.t = Text("Settings", [840, 40], 64, centered=True)

        self.zombie = load.image("zombie.png").convert_alpha()
        self.officer = load.image("officer.png").convert_alpha()
        self.house = load.image("house.png").convert_alpha()
        self.i = 0

    def update(self, loop):
        self.i += 1.5 * loop.get_ticktime()
        rotated = pygame.transform.rotate(self.zombie, math.sin(self.i) * 10)
        self.screen.blit(self.house, [-240,-270])
        self.screen.blit(self.officer, self.officer.get_rect(center=(300,500)))
        self.screen.blit(rotated, rotated.get_rect(center=(980,500)))

        self.t.draw(self.screen)

        
def main():
    pygame.init()
    pygame.mixer.init(buffer=512)
    screen = pygame.display.set_mode([1280, 720])
    pygame.display.set_caption("John Brawn")
    ready_tiles()

    game = Game(screen)
    menu = MainMenu(screen)
    settings = Settings(screen)
    scenedict = {"game": game, "menu": menu, "settings": settings}
    startscene = menu # switch around for debugging, default is "menu"
    soundManager = SoundManager(startscene.id)
    loop = Loop(screen, startscene, scenedict, soundManager)

    # populate "need to know" classes with loop reference
    Button.loop = loop
    TileMap.loop = loop
    
    loop.start()
