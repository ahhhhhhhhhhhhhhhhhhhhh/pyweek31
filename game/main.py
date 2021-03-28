from abc import ABC

import pygame
import pygame.freetype

import game.load as load
from game.map import TileMap

class Loop:
    def __init__(self, screen, scene, scenedict):
        self.scene = scene
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.scenedict = scenedict
        self.events = []

    def start(self):
        while True:
            self.events.clear()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.end_game()
                self.events.append(event)

            self.screen.fill((0,128,0))
            self.scene.update(self)
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
        self.screen.blit(self.image, (0,0))
        self.tmap.render(self.screen)
        

pygame.freetype.init()
font = pygame.freetype.Font(load.handle_path("lora/Lora-Bold.ttf"))

def render_text(text, size=16, color=(255,255,255)):
    return font.render(text, size=size, fgcolor=color)

def draw_text(screen, text, location, size=16, color=(255,255,255), centered=False):
    im, size = render_text(text, size, color)
    if centered:
        screen.blit(im, (location[0]-size[2]/2, location[1]))
    else:
        screen.blit(im, (location[0], location[1]))

class Text:
    def __init__(self, text, location, size=16, color=(255,255,255), centered=False):
        self.text = text
        self.location = location
        self.image = render_text(text, size, color)[0]
        self.centered = centered

        self.rect = pygame.Rect(self.location[0], self.location[1], self.image.get_width(), self.image.get_height())
        if self.centered:
            self.rect.x = self.location[0] - self.image.get_width() / 2

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Button(Text):
    def __init__(self, text, location, size=16, color=(255,255,255), centered=False):
        super().__init__(text, location, size, color, centered)
        self.clicked = False

    def draw(self, screen):
        super().draw(screen)
        self.clicked = False
        for event in Button.loop.get_events():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.rect.collidepoint(event.pos):
                    self.clicked = True

class MainMenu(Scene):
    def __init__(self, screen):
        self.screen = screen
        self.t = Text("hello world", [640, 40], 48, centered=True)
        self.b = Button("this is a button", [640, 110], 32, centered=True)

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
    loop = Loop(screen, menu, scenedict)
    Button.loop = loop #important
    loop.start()

    
        
