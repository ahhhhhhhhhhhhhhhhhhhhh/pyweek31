import json
import pygame
import game.load as load
import game.utils as utils


class SoundManager:
    instance = None

    def __init__(self, width, height):
        self.width, self.height = width, height
        self.sounds = [
            load.sound(),
            load.sound(),
        ]
        load.music()
        self.loadVolume()
        pygame.mixer.music.set_volume(self.musicVolume * self.masterVolume)
        for i in self.sounds:
            pygame.mixer.Sound.set_volume(i, self.masterVolume)
        self.playMusic()

        SoundManager.instance = self

    def playMusic(self):
        pygame.mixer.music.play(-1)

    def updateVolume(self, musicVolume, masterVolume):
        self.musicVolume = musicVolume
        self.masterVolume = masterVolume
        pygame.mixer.music.set_volume(self.musicVolume * self.masterVolume)
        self.saveVolume()
        for i in self.sounds:
            pygame.mixer.Sound.set_volume(i, self.masterVolume)

    def saveVolume(self):
        data = {
            "Volume": {
                "masterVolume": self.masterVolume,
                "musicVolume": self.musicVolume,
            }
        }
        with open(load.filepath("persistence.json"), "w") as write_file:
            json.dump(data, write_file)

    def loadVolume(self):
        with open(load.filepath("persistence.json"), "r") as read_file:
            data = json.load(read_file)
            self.masterVolume = data["Volume"]["masterVolume"]
            self.musicVolume = data["Volume"]["musicVolume"]