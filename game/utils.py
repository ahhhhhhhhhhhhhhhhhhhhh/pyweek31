import pygame

import game.load as load

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
