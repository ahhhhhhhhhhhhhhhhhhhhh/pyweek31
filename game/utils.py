import pygame
import pygame.freetype

import game.load as load
from game.sound import SoundEffectsManager as SoundManager

soundManager = SoundManager()
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
        self.settings = (size, color)

        self.rect = pygame.Rect(self.location[0], self.location[1], self.image.get_width(), self.image.get_height())
        if self.centered:
            self.rect.x = self.location[0] - self.image.get_width() / 2

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def update_text(self, newtext):
        self.image = render_text(newtext, *self.settings)[0]

        self.rect = pygame.Rect(self.location[0], self.location[1], self.image.get_width(), self.image.get_height())
        if self.centered:
            self.rect.x = self.location[0] - self.image.get_width() / 2

    def update_color(self, newcolor):
        self.settings = (self.settings[0], newcolor)
        self.update_text(self.text)

    def update_location(self, newloc):
        self.location = newloc
        self.rect.topleft = newloc

class TextButton(Text):
    def __init__(self, text, location, size=16, color=(255,255,255), centered=False):
        super().__init__(text, location, size, color, centered)
        self.clicked = False
        self.hovered = False

    def draw(self, screen):
        super().draw(screen)
        self.clicked = False
        for event in TextButton.loop.get_events():
            if event.type == pygame.MOUSEBUTTONDOWN and not getattr(event, "used", False) and event.button == 1:
                if self.rect.collidepoint(event.pos):
                    self.clicked = True
                    event.used = True
                    soundManager.playButtonSound()

        self.hovered = False
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.hovered = True
            TextButton.loop.request_cursor(pygame.SYSTEM_CURSOR_HAND)

    def update_location(self, newloc):
        self.location = newloc
        self.rect.topleft = newloc

class Button:
    #args are [pygame.Rect] or [location, surface]
    def __init__(self, *args):
        if len(args) == 1:
            self.rect = pygame.Rect(args[0])
        elif len(args) == 2:
            self.rect = pygame.Rect(args[0], args[1].get_size())
        else:
            raise TypeError("Wrong arguments")
        
    # says draw, but it just updates, nothing is shown onscreen
    def draw(self, screen):
        self.clicked = False
        for event in TextButton.loop.get_events():
            if event.type == pygame.MOUSEBUTTONDOWN and not getattr(event, "used", False) and event.button == 1:
                if self.rect.collidepoint(event.pos):
                    self.clicked = True
                    event.used = True
                    soundManager.playButtonSound()

        self.hovered = False
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.hovered = True
            TextButton.loop.request_cursor(pygame.SYSTEM_CURSOR_HAND)

    def update_location(self, newloc):
        self.location = newloc
        self.rect.topleft = newloc


#Button specifically meant for towers, could also be used for checkmarks and things
class ToggleButton(Button):
    def __init__(self, *args):
        super().__init__(*args)
        self.active = False

    def draw(self, screen):
        super().draw(self)

        if self.clicked:
            self.active = not self.active
