from abc import ABC
import math
import random

import pygame

import game.load as load
from game.map import TileMap, Start, Road, ready_tiles, Tower, FastTower, SniperTower, StunTower
from game.utils import Text, TextButton
from game.sound import MusicManager, SoundEffectsManager
from game.ui import TowerInfoPanel, BuyPanel, LevelSelectButton
import game.entity as entity

class Loop:
    def __init__(self, screen, scene, scenedict, musicManager):
        self.musicManager = musicManager
        self.soundManager = SoundEffectsManager()
        self.scene = scene
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.scenedict = scenedict
        self.events = []
        self.requested_cursor = None
        self.ticktime = 0
        self.fps_text = Text("", [10,10], color=(0,0,0))

    def start(self):
        while True:
            self.events.clear()
            self.requested_cursor = None
            for event in pygame.event.get():
                if (event.type == pygame.QUIT
                or (event.type == pygame.KEYDOWN and event.key == pygame.K_q
                and pygame.key.get_mods() & pygame.KMOD_CTRL)):
                    self.end_game()
                self.events.append(event)

            self.screen.fill((0,128,0))

            # this is where the magic happens
            self.scene.update(self)
            self.musicManager.update(self)

            self.handle_cursor()
            self.fps_text.update_text(str(round(self.clock.get_fps())))
            self.fps_text.draw(self.screen)
            
            pygame.display.flip()
            self.ticktime = self.clock.tick(144) / 1000
            self.ticktime = min(self.ticktime, 0.1)

    def switch_scene(self, new_scene):
        # new_scene is a Scene subclass or a string key
        if isinstance(new_scene, Scene):
            self.scene = new_scene
        else:
            self.scene = self.scenedict[new_scene]

    def get_scene(self, scene_key):
        return self.scenedict[scene_key]

    def end_game(self):
        pygame.quit()
        raise SystemExit

    def get_events(self):
        return self.events

    def request_cursor(self, cursor):
        self.requested_cursor = cursor

    def handle_cursor(self):
        if self.requested_cursor:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def get_ticktime(self):
        return self.ticktime

            
class Scene(ABC):
    def __init__(self, screen):
        self.screen = screen

    def update(self, loop):
        pass


class Game(Scene):
    def __init__(self, screen, bg_image_path, blocking_image_path, wave_txt_path):
        self.id = "game"
        self.screen = screen
        
        self.tmap = TileMap(load.image(bg_image_path), load.image(blocking_image_path))
        self.waves = entity.Waves(self, wave_txt_path, self.tmap)
        self.waves_display = Text("", [640,20], size=32, centered=True)
        self.waves_button = TextButton("[Call Next]", [640, 60], size=24, centered=True)

        self.tmap_offset = [25,25]
        self.zombies = []

        self.lives = 50
        self.display_lives = Text("", [1050, 10], size=32)

        self.currency = 300
        self.display_currency = Text("", [1050, 40], size=32)

        self.towers = []
        self.projectiles = []

        self.selected_tower = None
        self.tower_info_panel = TowerInfoPanel(self.screen, self.selected_tower, (1050, 75))

        self.buy_panel = BuyPanel(self.screen, (0, 545), [Tower(0,0), FastTower(0,0), SniperTower(0,0), StunTower(0,0)])
        self.build_mode = False
        self.towertypes = [Tower, FastTower, SniperTower, StunTower]
        self.selected_towertype = Tower
    
    def update(self, loop):
        deltatime = loop.get_ticktime()
        
        for event in loop.get_events():
            if event.type == pygame.KEYDOWN:
                # cheats
                if event.key == pygame.K_g:
                    self.currency += 100

        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_LEFT]:
            self.tmap_offset[0] += loop.get_ticktime() * 300
        if pressed[pygame.K_RIGHT]:
            self.tmap_offset[0] -= loop.get_ticktime() * 300
        if pressed[pygame.K_UP]:
            self.tmap_offset[1] += loop.get_ticktime() * 300
        if pressed[pygame.K_DOWN]:
            self.tmap_offset[1] -= loop.get_ticktime() * 300

        self.waves.update(self.zombies)
          
        self.tmap.render(self.screen, self.tmap_offset)

        wl, wp = self.waves.get_progress()
        self.waves_display.update_text(f"Wave {wl}/{wp}")
        self.waves_display.draw(self.screen)
        self.waves_button.draw(self.screen)
        if self.waves_button.clicked:
            self.waves.call_next(self.tmap)

        # updating lives/currency text
        self.display_lives.update_text("Lives: " + str(self.lives))
        self.display_lives.draw(self.screen)
        self.display_currency.update_text("Goodwill: " + str(self.currency))
        self.display_currency.draw(self.screen)

        tile = self.tmap.screen_to_tile_coords(pygame.mouse.get_pos())

        if tile:
            for event in loop.get_events():
                if event.type == pygame.MOUSEBUTTONDOWN and not getattr(event, "used", False) and event.button == 1:
                    event.used = True

                    # building/selecting towers
                    if isinstance(self.tmap.blocking[tile[0]][tile[1]], Tower):
                        self.build_mode = False
                        self.selected_tower = self.tmap.blocking[tile[0]][tile[1]]
                    else:
                        self.selected_tower = None

                    coords = self.tmap.tile_to_screen_coords(tile)
                    new_tower = self.selected_towertype(coords[0], coords[1])
                    if self.build_mode and self.tmap.can_build(tile) and self.currency >= new_tower.cost[0]:
                        print("building tower", tile)
                        loop.soundManager.playBuildingSound()
                        self.tmap.blocking[tile[0]][tile[1]] = new_tower
                        self.towers.append(new_tower)
                        self.currency -= new_tower.cost[0]

                # right click to exit build mode
                elif event.type == pygame.MOUSEBUTTONDOWN and not getattr(event, "used", False) and event.button == 3:
                    self.build_mode = False

        # highlights tiles if in build mode
        if self.build_mode and tile:
            coords = self.tmap.tile_to_screen_coords(tile)
            temp = self.selected_towertype(coords[0], coords[1])
            draw_coords = [coords[0] + self.tmap_offset[0], coords[1] + self.tmap_offset[1]]
            canbuild = self.tmap.can_build(tile)

            
            if canbuild:
                self.screen.blit(self.tmap.selector_open, draw_coords)
                pygame.draw.circle(self.screen, self.tmap.selector_open.get_at((0,0)), temp.center_pos(self.tmap_offset), temp.max_range, width=1)
            else:
                self.screen.blit(self.tmap.selector_closed, draw_coords)
                pygame.draw.circle(self.screen, self.tmap.selector_closed.get_at((0,0)), temp.center_pos(self.tmap_offset), temp.max_range, width=1)

        # updating tower info and buy panel
        if self.selected_tower != self.tower_info_panel.tower:
            self.tower_info_panel = TowerInfoPanel(self.screen, self.selected_tower, (1050, 75))
        self.currency = self.tower_info_panel.update(self.currency) # passes back any changes to currency becuase of upgrades
        self.tower_info_panel.draw(self.tmap_offset)

        self.buy_panel.update()
        self.buy_panel.draw()
        for i, b in enumerate(self.buy_panel.buttons):
            b = b.button
            if b.clicked:
                self.selected_towertype = self.towertypes[i]
                self.build_mode = True
                self.selected_tower = None

        # updating zombies and deleting zombies that reach end
        to_del = []
        for zombie in self.zombies:
            zombie.timestep(deltatime)
            zombie.render(self.screen, self.tmap_offset)
            if zombie.tile == None:
                to_del.append(zombie)
                self.lives -= 1
                loop.soundManager.playZombieEndSound()
        for zombie in to_del:
            self.zombies.remove(zombie)

        # updating towers
        for tower in self.towers:
            tower_pos = tower.center_pos(self.tmap_offset)
            
            if not tower.update(deltatime):
                continue

            in_range = []
            for z in self.zombies:
                z_pos = z.center_pos()
                dist = math.sqrt((z_pos[0] - tower_pos[0]) ** 2 + (z_pos[1] - tower_pos[1]) ** 2)
                if dist <= tower.max_range:
                    in_range.append(z)

            if len(in_range) == 0:
                continue

            # targets zombie closest to end
            target = min(in_range, key=lambda z: z.dist())

            self.projectiles.append(entity.BulletTrail(tower_pos, target.center_pos(), tower.bullet_color, tower.bullet_duration))
            tower.fire(target)
            target.hit(tower.damage)

            if isinstance(tower, StunTower):
                target.stun(tower.stun_duration)
                loop.soundManager.playTaserSound()

            if isinstance(tower, Tower):
                loop.soundManager.playBulletSound()

            if isinstance(tower, FastTower):
                loop.soundManager.playBulletSound()

            if isinstance(tower, SniperTower):
                loop.soundManager.playSniperSound()

            if target.is_dead():
                loop.soundManager.playZombieDeathSound()
                self.currency += target.reward
                self.zombies.remove(target)

        # updating projectiles
        to_del = []
        for p in self.projectiles:
            p.timestep(deltatime)
            p.render(self.screen)
            if p.is_done():
                to_del.append(p)
        for p in to_del:
            self.projectiles.remove(p)

        # game end conditions
        if self.lives < 1:
            loop.get_scene("endscreen").set_won(False, loop)
            loop.switch_scene("endscreen")
            loop.soundManager.playLevelLoseSound()

        if self.waves.get_finished() and not len(self.zombies):
            loop.get_scene("endscreen").set_won(True, loop)
            loop.switch_scene("endscreen")
            loop.soundManager.playLevelWinSound()

        # pausing
        for event in loop.get_events():
            if event.type == pygame.KEYDOWN and not getattr(event, "used", False) and event.key in [pygame.K_ESCAPE, pygame.K_p]:
                loop.get_scene("pause").set_return(self)
                loop.switch_scene("pause")
                event.used = True


class LevelSelect(Scene):
    def __init__(self, screen):
        self.screen = screen
        self.id = "level_select"

        self.title_text = Text("Level Select", [640, 40], 64, centered=True)

        self.city_image = load.image("very_very_bad_city_map.png")

        
        self.start_map = Game(screen, "maps/startmap_bg.png", "maps/startmap_blocking.png", "maps/startmap_waves.txt")
        self.map1 = Game(screen, "maps/map1_bg.png", "maps/map1_blocking.png", "maps/map1_waves.txt")
        self.onewavetest = Game(screen, "maps/startmap_bg.png", "maps/startmap_blocking.png", "maps/1wavetest.txt")
        self.rivermap = Game(screen, "maps/river_bg.png", "maps/river_blocking.png", "maps/1wavetest.txt")



        self.start_map_button = LevelSelectButton(self.screen, self.start_map, pygame.Rect(420, 200, 150, 200), "Start map")
        self.start_map_button.unlocked = True

        self.map1_button = LevelSelectButton(self.screen, self.map1, pygame.Rect(780, 175, 100, 100), "Map 1")
        self.map1_button.unlocked = True

        self.river_map_button = LevelSelectButton(self.screen, self.rivermap, pygame.Rect(600, 350, 200, 125), "River")
        self.river_map_button.unlocked = True

        self.onewavetest_b = LevelSelectButton(self.screen, self.onewavetest, pygame.Rect(500, 500, 50, 50), "1 wave")
        self.onewavetest_b.unlocked = True

        self.buttons = [self.start_map_button, self.map1_button, self.river_map_button, self.onewavetest_b]

        self.most_recent_played = None

    def update(self, loop):
        self.title_text.draw(self.screen)
        self.screen.blit(self.city_image, (400, 150))

        for b in self.buttons:
            b.update(loop)
            if b.unlocked and not b.completed and b.b.clicked:
                self.most_recent_played = b
                loop.switch_scene(b.level)
            b.draw()

        for event in loop.get_events():
            if event.type == pygame.KEYDOWN and not getattr(event, "used", False) and event.key in [pygame.K_ESCAPE, pygame.K_p]:
                loop.switch_scene("menu")
                event.used = True
    

class Pause(Scene):
    def __init__(self, screen):
        self.screen = screen
        self.id = "pause"
        self.title = Text("Paused", [640, 90], 90, centered=True)
        self.ret_button = TextButton("[Return to Game]", [640, 400], 40, centered=True)
        self.exit_button = TextButton("[Exit to Menu]", [640, 470], 40, centered=True)
        self.quit_button = TextButton("[Quit Game]", [640, 540], 40, centered=True)
        self.ret_scene = "game" #should be overwritten, this is merely a default

    def update(self, loop):
        self.title.draw(self.screen)
        self.ret_button.draw(self.screen)
        self.exit_button.draw(self.screen)
        self.quit_button.draw(self.screen)

        if self.exit_button.clicked:
            loop.switch_scene("menu")
        if self.quit_button.clicked:
            loop.end_game()
        if self.ret_button.clicked:
            loop.switch_scene(self.ret_scene)

        # unpausing via keyboard
        for event in loop.get_events():
            if event.type == pygame.KEYDOWN and not getattr(event, "used", False) and event.key in [pygame.K_ESCAPE, pygame.K_p]:
                loop.switch_scene(self.ret_scene)
                event.used = True

    def set_return(self, ret):
        self.ret_scene = ret

class EndScreen(Scene):
    def __init__(self, screen):
        self.screen = screen
        self.id = "endscreen"
        self.outcome_display = Text("", [640, 90], 90, centered=True)
        self.exit_button = TextButton("[Back to Map]", [640, 400], 40, centered=True)
        self.quit_button = TextButton("[Quit Game]", [640, 470], 40, centered=True)

    def update(self, loop):
        self.outcome_display.draw(self.screen)
        self.exit_button.draw(self.screen)
        self.quit_button.draw(self.screen)

        if self.exit_button.clicked:
            loop.switch_scene("level_select")
        if self.quit_button.clicked:
            loop.end_game()

    def set_won(self, won, loop):
        if won:
            self.outcome_display.update_text("You won!")
            loop.scenedict["level_select"].most_recent_played.completed = True
        else:
            self.outcome_display.update_text("You lost!")
            
class MainMenu(Scene):
    def __init__(self, screen):
        self.id = "menu"
        self.screen = screen
        self.t = Text("The Last Commissioner", [840, 40], 64, centered=True)
        self.b = TextButton("[Play if you dare...]", [840, 130], 32, centered=True)
        self.sb = TextButton("[Settings]", [840, 190], 32, centered=True)

        self.zombie = load.image("zombie.png").convert_alpha()
        self.officer = load.image("officer.png").convert_alpha()
        self.house = load.image("house.png").convert_alpha()
        self.i = 0

    def update(self, loop):
        self.i += 1.5 * loop.get_ticktime()
        rotated = pygame.transform.rotate(self.zombie, math.sin(self.i) * 10)
        self.screen.blit(self.house, [-240,-270])
        self.screen.blit(self.officer, self.officer.get_rect(center=(300,500)))
        self.screen.blit(rotated, rotated.get_rect(center=(980,500)))

        self.t.draw(self.screen)
        self.b.draw(self.screen)
        self.sb.draw(self.screen)

        if self.b.clicked:
            loop.switch_scene("level_select")
 
        if self.sb.clicked:
            loop.switch_scene("settings")

class Settings(Scene):
    def __init__(self, screen):
        self.id = "settings"
        self.screen = screen
        self.t = Text("Settings", [840, 40], 64, centered=True)
        self.musicText = Text("Music Volume:", [700, 130], 32, centered=True)
        self.soundText = Text("Sound Effects Volume:", [640, 190], 32, centered=True)
        self.musicVolumeText = Text("", [1000, 135], 32, centered = True)
        self.soundVolumeText = Text("", [1000, 195], 32, centered = True)
        self.musicLowerButton = TextButton("[-]", [900, 130], 32, centered=True)
        self.musicHigherButton = TextButton("[+]", [1100, 130], 32, centered=True)
        self.soundLowerButton = TextButton("[-]", [900, 190], 32, centered=True)
        self.soundHigherButton = TextButton("[+]", [1100, 190], 32, centered=True)
        self.leaveButton = TextButton("Return to Main Menu", [840, 250], 32, centered=True)

        self.zombie = load.image("zombie.png").convert_alpha()
        self.officer = load.image("officer.png").convert_alpha()
        self.house = load.image("house.png").convert_alpha()
        self.i = 0

    def update(self, loop):
        self.i += 1.5 * loop.get_ticktime()
        rotated = pygame.transform.rotate(self.zombie, math.sin(self.i) * 10)
        self.screen.blit(self.house, [-240,-270])
        self.screen.blit(self.officer, self.officer.get_rect(center=(300,500)))
        self.screen.blit(rotated, rotated.get_rect(center=(980,500)))

        self.musicVolumeText.update_text(str(round(loop.musicManager.volume*100)))
        self.soundVolumeText.update_text(str(round(loop.soundManager.volume*100)))

        self.t.draw(self.screen)
        self.musicText.draw(self.screen)
        self.soundText.draw(self.screen)
        self.musicVolumeText.draw(self.screen)
        self.soundVolumeText.draw(self.screen)
        self.musicLowerButton.draw(self.screen)
        self.musicHigherButton.draw(self.screen)
        self.soundLowerButton.draw(self.screen)
        self.soundHigherButton.draw(self.screen)
        self.leaveButton.draw(self.screen)

        if self.musicLowerButton.clicked:
           loop.musicManager.changeVolume(-.05)
        elif self.musicHigherButton.clicked:
            loop.musicManager.changeVolume(.05)
        elif self.soundLowerButton.clicked:
            loop.soundManager.changeVolume(-.05)
        elif self.soundHigherButton.clicked:
            loop.soundManager.changeVolume(.05)
        elif self.leaveButton.clicked:
            loop.switch_scene("menu")

        for event in loop.get_events():
            if event.type == pygame.KEYDOWN and not getattr(event, "used", False) and event.key in [pygame.K_ESCAPE, pygame.K_p]:
                loop.switch_scene("menu")
                event.used = True


        
def main():
    pygame.init()
    screen = pygame.display.set_mode([1280, 720])
    pygame.display.set_caption("The Last Commissioner")
    ready_tiles()

    menu = MainMenu(screen)
    level_select = LevelSelect(screen)
    settings = Settings(screen)
    endscreen = EndScreen(screen)
    pause = Pause(screen)
    scenedict = {"menu": menu, "level_select": level_select,
                 "settings": settings, "endscreen": endscreen,
                 "pause": pause}
    startscene = menu # switch around for debugging, default is "menu"
    musicManager = MusicManager(startscene.id)
    loop = Loop(screen, startscene, scenedict, musicManager)

    # populate "need to know" classes with loop reference
    TextButton.loop = loop
    TileMap.loop = loop
    entity.Waves.loop = loop
    
    loop.start()
