import textwrap

import pygame
import pygame.freetype

import game.load as load
from game.sound import SoundEffectsManager as SoundManager

pygame.freetype.init()
font = pygame.freetype.Font(load.handle_path("lora/Lora-Bold.ttf"))

DEFAULT_HOVERCOLOR = (187,10,30)
DEFAULT_TEXTSIZE = 16
DEFAULT_TEXTCOLOR = (255,255,255)

def render_text(text, size=DEFAULT_TEXTSIZE, color=DEFAULT_TEXTCOLOR):
    return font.render(text, size=size, fgcolor=color)

def draw_text(screen, text, location, size=DEFAULT_TEXTSIZE, color=DEFAULT_TEXTCOLOR, centered=False):
    im, size = render_text(text, size, color)
    if centered:
        screen.blit(im, (location[0]-size[2]/2, location[1]))
    else:
        screen.blit(im, (location[0], location[1]))

class Text:
    def __init__(self, text, location, size=DEFAULT_TEXTSIZE, color=DEFAULT_TEXTCOLOR, centered=False):
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
    def __init__(self, text, location, size=DEFAULT_TEXTSIZE, color=DEFAULT_TEXTCOLOR, centered=False):
        super().__init__(text, location, size, color, centered)
        self.clicked = False
        self.hovered = False
        self._washovered = False
        self._hovercolor = DEFAULT_HOVERCOLOR
        self._originalcolor = None

    def draw(self, screen):
        super().draw(screen)
        self.clicked = False
        for event in TextButton.loop.get_events():
            if event.type == pygame.MOUSEBUTTONDOWN and not getattr(event, "used", False) and event.button == 1:
                if self.rect.collidepoint(event.pos):
                    self.clicked = True
                    event.used = True
                    TextButton.loop.soundManager.playButtonSound()

        self.hovered = False
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.hovered = True
            TextButton.loop.request_cursor(pygame.SYSTEM_CURSOR_HAND)

        # hover on
        if self._hovercolor and self.hovered and not self._washovered:
            self._washovered = True
            self._originalcolor = self.settings[1]
            self.update_color(self._hovercolor)
        # hover off
        if self._washovered and not self.hovered:
            self._washovered = False
            self.update_color(self._originalcolor)

    def update_location(self, newloc):
        self.location = newloc
        self.rect.topleft = newloc

    def set_hovercolor(self, col):
        self._hovercolor = col

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
                    #soundManager.playButtonSound()

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

# quick and dirty multiline text
class LinedText:
    def __init__(self, text, location, n_charwrap, spacing=1.5, size=DEFAULT_TEXTSIZE, color=DEFAULT_TEXTCOLOR):
        self.text = text
        self.location = location
        self.spacing = spacing
        self.images = [render_text(t, size, color)[0] for t in textwrap.wrap(text, n_charwrap)]        

        #self.rect = pygame.Rect(self.location[0], self.location[1], self.image.get_width(), self.image.get_height())

    def draw(self, screen):
        x = self.location[0]
        y = self.location[1]
        for i, image in enumerate(self.images):
            screen.blit(image, (x, y))
            y += image.get_height() * self.spacing
            
    def update_location(self, newloc):
        self.location = newloc
        self.rect.topleft = newloc
