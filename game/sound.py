import json
import io
import pygame
import game.load as load

class MusicManager:
    def __init__(self, scene):
        self.scene = scene
        self.sounds = [
            load.sound("sound_files/buttonSound.wav"),
        ]
        data = self.loadVolume()
        self.volume = data["Volume"]["musicVolume"]
        pygame.mixer.music.set_volume(self.volume)
        for i in self.sounds:
            pygame.mixer.Sound.set_volume(i, self.volume)
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

    def updateVolume(self, musicVolume):
        self.volume = musicVolume
        pygame.mixer.music.set_volume(self.volume)
        self.saveVolume()

    def saveVolume(self):
        data = loadVolume()
        data["Volume"]["musicVolume"] = self.volume
        with open(load.handle_path("persistence.json"), "w") as write_file:
            json.dump(data, write_file)

    def loadVolume(self):
        if load.path_exists("persistence.json"):
            with open(load.handle_path("persistence.json"), "r") as read_file:
                return json.load(read_file)
        else:
            with io.open(load.handle_path("persistence.json"), "w") as write_file:
                data = {"Volume": {"musicVolume": 1, "soundVolume": 1}}
                write_file.write(json.dump(data))   
            with open(load.handle_path("persistence.json"), "r") as read_file:
                return json.load(read_file)

    def update(self, loop):
        if loop.scene.id != self.scene:
            self.scene = loop.scene.id
            if self.scene == "game":
                self.playGameMusic()
            elif self.scene == "menu":
                self.playMenuMusic()

class SoundEffectsManager:
    def __init__(self):
        pygame.mixer.init(buffer=512)
        self.sounds = [
            load.sound("sound_files/buttonSound.wav"),
        ]
        data = self.loadVolume()
        self.volume = data["Volume"]["soundVolume"]
        for i in self.sounds:
            pygame.mixer.Sound.set_volume(i, self.volume)

    def playButtonSound(self):
        pygame.mixer.Sound.play(self.sounds[0])

    def updateVolume(self, soundVolume):
        self.volume = soundVolume
        for i in self.sounds:
            pygame.mixer.Sound.set_volume(i, self.volume)
        self.saveVolume()

    def saveVolume(self):
        data = loadVolume()
        data["Volume"]["soundVolume"] = self.volume
        with open(load.handle_path("persistence.json"), "w") as write_file:
            json.dump(data, write_file)

    def loadVolume(self):
        if load.path_exists("persistence.json"):
            with open(load.handle_path("persistence.json"), "r") as read_file:
                return json.load(read_file)
        else:
            with io.open(load.handle_path("persistence.json"), "w") as write_file:
                data = {"Volume": {"musicVolume": 1, "soundVolume": 1}}
                write_file.write(json.dumps(data))   
            with open(load.handle_path("persistence.json"), "r") as read_file:
                return json.load(read_file)