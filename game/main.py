from abc import ABC

import pygame
import pygame.freetype

import math

import game.load as load
from game.map import TileMap, Start, Road, Tower, NoBlocking, ready_tiles
from game.utils import Text, Button

class Loop:
    def __init__(self, screen, scene, scenedict):
        self.scene = scene
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.scenedict = scenedict
        self.events = []
        self.requested_cursor = None

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
            self.scene.update(self)
            self.handle_cursor()
            pygame.display.flip()
            self.clock.tick(144)

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

            
class Scene(ABC):
    def __init__(self, screen):
        self.screen = screen

    def update(self, loop):
        pass

class Game(Scene):
    def __init__(self, screen):
        self.screen = screen
        
        self.tmap = TileMap(load.image("map.png"))
        for tile in self.tmap.starts:
            while type(tile) in (Start,Road):
                # print (tile)
                tile = tile.next
            # print ()

        self.tmap_offset = [60,60]
        
    def update(self, loop):
        self.tmap.render(self.screen, self.tmap_offset)

        for event in loop.get_events():
            if event.type == pygame.MOUSEBUTTONDOWN and not getattr(event, "used", False):
                event.used = True
                selected_tile = self.tmap.screen_to_tile_coords(event.pos)
                
                if selected_tile and self.can_build(selected_tile):  
                    print("building tower", selected_tile)

                    coords = self.tmap.tile_to_screen_coords(selected_tile)
                    self.tmap.blocking[selected_tile[0]][selected_tile[1]] = Tower(coords[0], coords[1])

    def can_build(self, tile):
        return isinstance(self.tmap.blocking[tile[0]][tile[1]], NoBlocking) and not isinstance(self.tmap.map[tile[0]][tile[1]], Road)

            
class MainMenu(Scene):
    def __init__(self, screen):
        self.screen = screen
        self.t = Text("John Brawn", [640, 40], 48, centered=True)
        self.b = Button("Play if you dare...", [640, 110], 32, centered=True)

        self.zombie = load.image("zombie.png").convert_alpha()
        self.i = 0

    def update(self, loop):
        self.t.draw(self.screen)
        self.b.draw(self.screen)

        self.i += 0.01
        rotated = pygame.transform.rotate(self.zombie, math.sin(self.i) * 10)
        self.screen.blit(rotated, (200,50))
        self.screen.blit(rotated, (800,50))

        if self.b.clicked:
            loop.switch_scene("game")

        
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
    Button.loop = loop
    loop.start()
