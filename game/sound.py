import json
import pygame
import game.load as load
import game.utils as utils


class SoundManager:
    def __init__(self, scene):
        self.scene = scene
        self.sounds = [
            load.sound("sound_files/buttonSound.wav"),
        ]
        self.loadVolume()
        pygame.mixer.music.set_volume(self.musicVolume * self.masterVolume)
        for i in self.sounds:
            pygame.mixer.Sound.set_volume(i, self.masterVolume)
        if self.scene == "game":
            self.playGameMusic()
        elif self.scene == "menu":
            self.playMenuMusic()

    def playMenuMusic(self):
        pygame.mixer.music.load(load.handle_path("sound_files/menuMusic.ogg"))
        pygame.mixer.music.play(-1)

    def playGameMusic(self):
        pygame.mixer.music.load(load.handle_path("sound_files/gameMusic.ogg"))
        pygame.mixer.music.play(-1)

    def playButtonSound(self):
        pygame.mixer.Sound.play(self.sounds[0])

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
        with open(load.handle_path("persistence.json"), "w") as write_file:
            json.dump(data, write_file)

    def loadVolume(self):
        with open(load.handle_path("persistence.json"), "r") as read_file:
            data = json.load(read_file)
            self.masterVolume = data["Volume"]["masterVolume"]
            self.musicVolume = data["Volume"]["musicVolume"]

    def update(self, loop):
        if loop.scene.id != self.scene:
            self.scene = loop.scene.id
            if self.scene == "game":
                self.playGameMusic()
            elif self.scene == "menu":
                self.playMenuMusic()