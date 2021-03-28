import os

import pygame

path = "data"

def image(filepath):
    filepath = os.path.join(path, filepath)
    return pygame.image.load(filepath)
