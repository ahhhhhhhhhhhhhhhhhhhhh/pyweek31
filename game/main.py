from abc import ABC
import math
import random

import pygame

import game.load as load
from game.map import TileMap, Start, Road, ready_tiles, Tower, FastTower
from game.utils import Text, TextButton
from game.sound import MusicManager
from game.ui import TowerInfoPanel
import game.entity as entity

class Loop:
    def __init__(self, screen, scene, scenedict, musicManager):
        self.musicManager = musicManager
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
                or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE)):
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
    def __init__(self, screen):
        self.id = "game"
        self.screen = screen
        
        self.tmap = TileMap(load.image("maps/map1_bg.png"), load.image("maps/map1_blocking.png"))
        self.waves = entity.Waves("maps/map1_waves.txt", self.tmap)

        self.tmap_offset = [25,25]
        self.zombies = []

        self.lives = 50
        self.display_lives = Text("", [1100, 20], size=32)

        self.towers = []
        self.projectiles = []

        self.selected_tower = None
        self.tower_info_panel = TowerInfoPanel(self.screen, self.selected_tower, (1050, 100))

        self.build_mode = False
        self.selected_towertype = Tower
        self.tower_button = TextButton("Station Additional Officer", [40, 620], 25)
        self.fast_tower_button = TextButton("Station Additional Fast Officer", [40, 660], 25)
    
    def update(self, loop):
        deltatime = loop.get_ticktime()
        
        for event in loop.get_events():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                self.waves.call_next(self.tmap)

        self.waves.update(self.zombies)
          
        self.tmap.render(self.screen, self.tmap_offset)

        # updating lives text
        self.display_lives.update_text("Lives: " + str(self.lives))
        self.display_lives.draw(self.screen)

        # updating tower buying buttons
        self.tower_button.draw(self.screen)
        self.fast_tower_button.draw(self.screen)
        if self.tower_button.clicked:
            self.selected_towertype = Tower
            self.build_mode = True
            self.selected_tower = None
        elif self.fast_tower_button.clicked:
            self.selected_towertype = FastTower
            self.build_mode = True
            self.selected_tower = None

        # updating tower info panel
        if self.selected_tower != self.tower_info_panel.tower:
            self.tower_info_panel = TowerInfoPanel(self.screen, self.selected_tower, (1050, 100))
        self.tower_info_panel.update()
        self.tower_info_panel.draw()


        tile = self.tmap.screen_to_tile_coords(pygame.mouse.get_pos())

        if tile:
            for event in TileMap.loop.get_events():
                if event.type == pygame.MOUSEBUTTONDOWN and not getattr(event, "used", False) and event.button == 1:
                    event.used = True

                    # building/selecting towers
                    if isinstance(self.tmap.blocking[tile[0]][tile[1]], Tower):
                        self.build_mode = False
                        self.selected_tower = self.tmap.blocking[tile[0]][tile[1]]
                    else:
                        self.selected_tower = None

                    if self.build_mode and self.tmap.can_build(tile):
                        print("building tower", tile)
                        coords = self.tmap.tile_to_screen_coords(tile)
                        new_tower = self.selected_towertype(coords[0], coords[1])
                        self.tmap.blocking[tile[0]][tile[1]] = new_tower
                        self.towers.append(new_tower)

                # right click to exit build mode
                elif event.type == pygame.MOUSEBUTTONDOWN and not getattr(event, "used", False) and event.button == 3:
                    self.build_mode = False

        # highlights tiles if in build mode
        if self.build_mode and tile:
            coords = self.tmap.tile_to_screen_coords(tile)
            canbuild = self.tmap.can_build(tile)

            temp = self.selected_towertype(coords[0], coords[1])
            if canbuild:
                self.screen.blit(self.tmap.selector_open, coords)
                pygame.draw.circle(self.screen, self.tmap.selector_open.get_at((0,0)), temp.center_pos(), temp.max_range, width=1)
            else:
                self.screen.blit(self.tmap.selector_closed, coords)
                pygame.draw.circle(self.screen, self.tmap.selector_closed.get_at((0,0)), temp.center_pos(), temp.max_range, width=1)

        # updating zombies and deleting zombies that reach end
        to_del = []
        for zombie in self.zombies:
            zombie.timestep(deltatime)
            zombie.render(self.screen, self.tmap_offset)
            if zombie.tile == None:
                to_del.append(zombie)
                self.lives -= 1
        for zombie in to_del:
            self.zombies.remove(zombie)

        # updating towers
        for tower in self.towers:
            tower_pos = tower.center_pos()
            
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

            self.projectiles.append(entity.BulletTrail(tower_pos, target.center_pos(), tower.bullet_color))
            tower.fire(target)
            target.hit(tower.damage)
            if target.is_dead():
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
            loop.get_scene("endscreen").set_won(False)
            loop.switch_scene("endscreen")
    

class EndScreen(Scene):
    def __init__(self, screen):
        self.screen = screen
        self.id = "endscreen"
        self.outcome_display = Text("", [640, 90], 90, centered=True)
        self.exit_button = TextButton("[Exit to Menu]", [640, 400], 40, centered=True)
        self.quit_button = TextButton("[Quit Game]", [640, 470], 40, centered=True)

    def update(self, loop):
        self.outcome_display.draw(self.screen)
        self.exit_button.draw(self.screen)
        self.quit_button.draw(self.screen)

        if self.exit_button.clicked:
            loop.switch_scene("menu")
        if self.quit_button.clicked:
            loop.end_game()

    def set_won(self, won):
        if won:
            self.outcome_display.update_text("You won!")
        else:
            self.outcome_display.update_text("You lost!")        
            
class MainMenu(Scene):
    def __init__(self, screen):
        self.id = "menu"
        self.screen = screen
        self.t = Text("John Brawn", [840, 40], 64, centered=True)
        self.b = TextButton("[Play if you dare...]", [840, 130], 32, centered=True)
        self.sb = TextButton("Settings", [840, 190], 32, centered=True)

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
            loop.switch_scene("game")
 
        if self.sb.clicked:
            loop.switch_scene("settings")

class Settings(Scene):
    def __init__(self, screen):
        self.id = "settings"
        self.screen = screen
        self.t = Text("Settings", [840, 40], 64, centered=True)

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

        
def main():
    pygame.init()
    screen = pygame.display.set_mode([1280, 720])
    pygame.display.set_caption("John Brawn")
    ready_tiles()

    game = Game(screen)
    menu = MainMenu(screen)
    settings = Settings(screen)
    endscreen = EndScreen(screen)
    scenedict = {"game": game, "menu": menu, "settings": settings, "endscreen": endscreen}
    startscene = menu # switch around for debugging, default is "menu"
    musicManager = MusicManager(startscene.id)
    loop = Loop(screen, startscene, scenedict, musicManager)

    # populate "need to know" classes with loop reference
    TextButton.loop = loop
    TileMap.loop = loop
    entity.Waves.loop = loop
    
    loop.start()
