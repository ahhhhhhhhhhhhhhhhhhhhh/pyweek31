import json
import io
import pygame
import game.load as load

class MusicManager:
    def __init__(self, scene):
        pygame.mixer.init(buffer=512)
        self.scene = scene
        data = self.loadVolume()
        self.volume = data["Volume"]["musicVolume"]
        pygame.mixer.music.set_volume(self.volume)
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

    def changeVolume(self, changingValue):
        self.volume = self.volume + changingValue
        if self.volume > 1:
            self.volume = 1
        elif self.volume < 0:
            self.volume = 0
        pygame.mixer.music.set_volume(self.volume)
        self.saveVolume()

    def updateVolume(self, musicVolume):
        self.volume = musicVolume
        pygame.mixer.music.set_volume(self.volume)
        self.saveVolume()

    def saveVolume(self):
        data = self.loadVolume()
        data["Volume"]["musicVolume"] = self.volume
        with open(load.handle_path("persistence.json"), "w") as write_file:
            json.dump(data, write_file)

    def loadVolume(self):
        if load.path_exists("persistence.json"):
            rewriteData = False
            data = None
            with open(load.handle_path("persistence.json"), "r") as read_file:
                try: 
                    data = json.load(read_file)
                except:
                    rewriteData = True
            if rewriteData or (not load.check_value_exist(data, "Volume")):
                with io.open(load.handle_path("persistence.json"), "w") as write_file:
                    data = {"Volume": {"musicVolume": 1, "soundVolume": 1}}
                    json.dump(data, write_file)
            return data
        else:
            with io.open(load.handle_path("persistence.json"), "w") as write_file:
                data = {"Volume": {"musicVolume": 1, "soundVolume": 1}}
                json.dump(data, write_file)   
            with open(load.handle_path("persistence.json"), "r") as read_file:
                return json.load(read_file)

    def update(self, loop):
        if loop.scene.id != self.scene:
            if loop.scene.id == "game" and self.scene != "pause":
                self.playGameMusic()
            elif ((loop.scene.id == "menu" or loop.scene.id == "settings" or loop.scene.id == "level_select") 
                    and self.scene == "pause" or self.scene == "endscreen"):
                self.playMenuMusic()
            self.scene = loop.scene.id

    def fadeout(self, fadeoutTime):
        pygame.mixer.music.fadeout(fadeoutTime)

class SoundEffectsManager:
    def __init__(self):
        pygame.mixer.init(buffer=512)
        self.sounds = [
            load.sound("sound_files/buttonSound.wav"),
            load.sound("sound_files/buildingSound.wav"),
            load.sound("sound_files/bulletSound.wav"),
            load.sound("sound_files/zombieDeathSound.wav"),
            load.sound("sound_files/zombieEndSound.wav"),
            load.sound("sound_files/taserSound.wav"),
            load.sound("sound_files/sniperSound.wav"),
            load.sound("sound_files/levelWinSound.wav"),
            load.sound("sound_files/levelLoseSound.wav"),
            load.sound("sound_files/failSound.wav"),
        ]
        self.soundmap = { 
            "button" : self.sounds[0],
            "building" : self.sounds[1],
            "bullet" : self.sounds[2],
            "zombie_death" : self.sounds[3],
            "zombie_end" : self.sounds[4],
            "taser" : self.sounds[5],
            "sniper" : self.sounds[6],
            "level_win" : self.sounds[7],
            "level_lose" : self.sounds[8],
            "fail" : self.sounds[9],
        }
        data = self.loadVolume()
        self.volume = data["Volume"]["soundVolume"]
        for i in self.sounds:
            pygame.mixer.Sound.set_volume(i, self.volume)

    def playSound(self, name):
        pygame.mixer.Sound.play(self.soundmap[name])

    def playButtonSound(self):
        pygame.mixer.Sound.play(self.sounds[0])

    def playBuildingSound(self):
        pygame.mixer.Sound.play(self.sounds[1])
    
    def playBulletSound(self):
        pygame.mixer.Sound.play(self.sounds[2])

    def playZombieDeathSound(self):
        pygame.mixer.Sound.play(self.sounds[3])
    
    def playZombieEndSound(self):
        pygame.mixer.Sound.play(self.sounds[4])

    def playTaserSound(self):
        pygame.mixer.Sound.play(self.sounds[5])

    def playSniperSound(self):
        pygame.mixer.Sound.play(self.sounds[6])

    def playLevelWinSound(self):
        pygame.mixer.Sound.play(self.sounds[7])

    def playLevelLoseSound(self):
        pygame.mixer.Sound.play(self.sounds[8])

    def playFailSound(self):
        pygame.mixer.Sound.play(self.sounds[9])

    def stopSound(self):
        for i in self.sounds:
            pygame.mixer.Sound.stop(i)

    def changeVolume(self, changingValue):
        self.volume = self.volume + changingValue
        if self.volume > 1:
            self.volume = 1
        elif self.volume < 0:
            self.volume = 0
        for i in self.sounds:
            pygame.mixer.Sound.set_volume(i, self.volume)
        self.saveVolume()

    def updateVolume(self, soundVolume):
        self.volume = soundVolume
        for i in self.sounds:
            pygame.mixer.Sound.set_volume(i, self.volume)
        self.saveVolume()

    def saveVolume(self):
        data = self.loadVolume()
        data["Volume"]["soundVolume"] = self.volume
        with open(load.handle_path("persistence.json"), "w") as write_file:
            json.dump(data, write_file)

    def loadVolume(self):
        if load.path_exists("persistence.json"):
            rewriteData = False
            data = None
            with open(load.handle_path("persistence.json"), "r") as read_file:
                try: 
                    data = json.load(read_file)
                except:
                    rewriteData = True
            if rewriteData or (not load.check_value_exist(data, "Volume")):
                with io.open(load.handle_path("persistence.json"), "w") as write_file:
                    data = {"Volume": {"musicVolume": 1, "soundVolume": 1}}
                    json.dump(data, write_file)
            return data
        else:
            with io.open(load.handle_path("persistence.json"), "w") as write_file:
                data = {"Volume": {"musicVolume": 1, "soundVolume": 1}}
                json.dump(data, write_file)   
            with open(load.handle_path("persistence.json"), "r") as read_file:
                return json.load(read_file)