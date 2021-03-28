import os

import pygame

PATH = "data"

def handle_path(filepath):
    filepath = os.path.split(filepath)
    filepath = os.path.join(PATH, *filepath)
    return filepath

def image(filepath):
    filepath = handle_path(filepath)
    return pygame.image.load(filepath)
