from abc import ABC

import pygame

import game.load as load

class Loop:
    def __init__(self, screen, scene):
        self.scene = scene
        self.screen = screen
        self.clock = pygame.time.Clock()

    def start(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.end_game()


            self.screen.fill((0,0,0))
            self.scene.update(self)
            pygame.display.flip()
            self.clock.tick(144)

    def switch_scene(self, new_scene):
        self.scene = new_scene

    def end_game(self):
        pygame.quit()
        raise SystemExit
            
class Scene(ABC):
    def __init__(self, screen):
        self.screen = screen

    def update(self, loop):
        pass

class Game(Scene):
    def __init__(self, screen):
        self.screen = screen
        self.image = load.image("zombie.png").convert_alpha()
    
    def update(self, loop):
        self.screen.blit(self.image, (0,0))

def main():
    pygame.init()
    screen = pygame.display.set_mode([1280, 720])

    game = Game(screen)
    loop = Loop(screen, game)
    loop.start()

    
        
