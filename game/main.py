from abc import ABC

import pygame
import pygame.freetype

import game.load as load
from game.map import TileMap
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
                if event.type == pygame.QUIT:
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
        self.image = load.image("zombie.png").convert_alpha()
        
        self.tmap = TileMap(load.image("map.png"))
        
    def update(self, loop):
        self.screen.blit(self.image, (900,20))
        self.tmap.render(self.screen, [60,60])
        

class MainMenu(Scene):
    def __init__(self, screen):
        self.screen = screen
        self.t = Text("John Brawn", [640, 40], 48, centered=True)
        self.b = Button("Play if you dare...", [640, 110], 32, centered=True)

    def update(self, loop):
        self.t.draw(self.screen)
        self.b.draw(self.screen)

        if self.b.clicked:
            loop.switch_scene("game")
        
def main():
    pygame.init()
    screen = pygame.display.set_mode([1280, 720])
    pygame.display.set_caption("John Brawn")

    game = Game(screen)
    menu = MainMenu(screen)
    scenedict = {"game": game, "menu": menu}
    startscene = menu # switch around for debugging, default is "menu"
    loop = Loop(screen, startscene, scenedict)
    Button.loop = loop
    loop.start()
