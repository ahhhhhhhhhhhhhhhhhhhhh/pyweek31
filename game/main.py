from abc import ABC

import pygame

import math

import game.load as load
from game.map import TileMap, Start, Road, ready_tiles
from game.utils import Text, Button

class Loop:
    def __init__(self, screen, scene, scenedict):
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
            self.handle_cursor()
            self.fps_text.update_text(str(round(self.clock.get_fps())))
            self.fps_text.draw(self.screen)
            
            pygame.display.flip()
            self.ticktime = self.clock.tick(144) / 1000

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
        self.screen = screen
        
        self.tmap = TileMap(load.image("map.png"))

        #should this be the tilemap itself?
        for tile in self.tmap.starts:
            while type(tile) in (Start,Road):
                tile = tile.next

        self.tmap_offset = [60,60]
        
    def update(self, loop):
        self.tmap.render(self.screen, self.tmap_offset)

            
class MainMenu(Scene):
    def __init__(self, screen):
        self.screen = screen
        self.t = Text("John Brawn", [840, 40], 64, centered=True)
        self.b = Button("[Play if you dare...]", [840, 130], 32, centered=True)
        self.b.washovered = False

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

        if self.b.clicked:
            loop.switch_scene("game")

        if self.b.hovered:
            self.b.update_color((128,255,0))
            self.b.washovered = True
        elif self.b.washovered:
            self.b.update_color((255,255,255))

        
def main():
    pygame.init()
    pygame.mixer.init(buffer=512)
    screen = pygame.display.set_mode([1280, 720])
    pygame.display.set_caption("John Brawn")
    ready_tiles()

    game = Game(screen)
    menu = MainMenu(screen)
    scenedict = {"game": game, "menu": menu}
    startscene = menu # switch around for debugging, default is "menu"
    loop = Loop(screen, startscene, scenedict)

    # populate "need to know" classes with loop reference
    Button.loop = loop
    TileMap.loop = loop
    
    loop.start()
