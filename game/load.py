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

def sound(filepath):
    filepath = handle_path(filepath)
    return pygame.mixer.Sound(filepath)

def path_exists(filepath):
    path = handle_path(filepath)
    print(os.path.exists(path))
    return os.path.exists(path)