from abc import ABC
import random
random.seed(10)

import pygame

import game.load as load
import game.utils as utils
from game.projectile import BulletTrail, Grenade

SCALE = 50

# Abstract class fot every thing on the grid
class Tile(ABC):
    xdim = 1
    ydim = 1
    #passes in x and y pos
    def __init__(self, x, y):
        self.x, self.y = x, y
    
    #renders at screen pos (Not tile grid pos)
    def render(self, screen, x, y, offset):
        if self.image != None:
            screen.blit(self.image, (x + offset[0], y + offset[1]))
    
    #stuff that needs to happen after map creation
    def link(self, tilemap, x, y):
        pass

class MultiTile(Tile):
    xdim = 1
    ydim = 1
    
    def __init__(self, x, y):
        super().__init__(x, y)
        self.corner = False
    
    def link(self, tilemap, x, y):
        distx = 0
        while type(tilemap[x-distx-1, y]) == type(self):
            distx += 1
        
        disty = 0
        while type(tilemap[x, y-disty-1]) == type(self):
            disty += 1
        
        
        if distx%self.xdim == 0 and disty%self.ydim == 0:
            self.corner = True
            for ox in range(self.xdim):
                for oy in range(self.ydim):
                    if (type(tilemap[self.x+ox, self.y+oy]) != type(self)):
                        tilemap.map[self.x+ox][self.y+oy] = type(self)(self.x+ox, self.y+oy)
    
    def render(self, screen, x, y, offset):
        if self.corner:
            super().render(screen, x, y, offset)

class NoTile(Tile):
    image = None


class Grass(Tile):
    pass

class Sand(Tile):
    pass

class Sidewalk(Tile):
    pass


# This class connects same tiles together
# the images class constant should set a list of all possible connections
# in the order:   -, '-, ---, -'-, -|-
class Touching(Tile):
    touchgroup = None
    def link(self, tilemap, gx, gy):
        dirs = []
        for ox,oy in [(1,0),(0,-1),(-1,0),(0,1)]:
            tile = tilemap[gx+ox,gy+oy]
            issame = (not self.touchgroup and type(tile) == type(self)) or type(tile) in self.touchgroup
            dirs.append('1' if issame else '0')
        
        for rot in range(4):
            strdir = ''.join(dirs[rot:]) + ''.join(dirs[:rot])
            
            num = int(strdir[::-1], 2)
            if num in (1,3,5,7,15):
                img = self.images[(1,3,5,7,15).index(num)]
                self.image = pygame.transform.rotate(img, 90*rot)
                return

#
# class Bordered(Tile):
#     borderes = {}
#     base = None
#     images = []
#
#     def init_images():
#         self.images = []
#         for sides in range(int("1111", 2)):
#


class Road(Touching):
    # image = pygame.Surface((SCALE,SCALE))
    # image.fill((64,64,64))
    images = [
        load.image("road01.png"),
        load.image("road03.png"),
        load.image("road05.png"),
        load.image("road07.png"),
        load.image("road15.png"),
    ]
    
    def __init__(self, x, y):
        super().__init__(x, y)
        self.next = {}
    
    #recursively sets next pointers for roads
    def setnext(self, newnext, tilemap, endgoal, dist, x, y):
        self.next[endgoal] = (newnext, dist)
        End.setnext(self, tilemap, endgoal, dist, x, y)

class End(Tile):
    image = pygame.Surface((SCALE,SCALE))
    image.fill((0,38,255))
    
    
    # decides path for road tiles
    def link(self, tilemap, gx, gy):
        self.setnext(tilemap, self, 0, gx, gy)
    
    def setnext(self, tilemap, endgoal, dist, gx, gy):
        for ox,oy in [(-1,0),(0,-1),(1,0),(0,1)]:
            tile = tilemap[gx+ox,gy+oy]
            if (type(tile) in (Road, Start) and endgoal not in tile.next):
                tile.setnext(self, tilemap, endgoal, dist+1, gx+ox, gy+oy)

class Start(Road):
    image = pygame.Surface((SCALE, SCALE))
    image.fill((255,0,0))
    touchgroup = []
    
    def setnext(self, newnext, tilemap, endgoal, dist, x, y):
        self.next[endgoal] = (newnext, dist)

class House(Tile):
    pass

class HouseVariant1(House):
    pass

class BrickHouse(House):
    pass

class BridgeRoad(Road):
    pass

class BridgeGrate(Tile):
    pass

class BridgePillars(Tile):
    pass

class Bridge(MultiTile):
    xdim = 1
    ydim = 5

class BigHouse(MultiTile):
    xdim = 2
    ydim = 2

class BigHouse2(BigHouse):
    pass

class BigHouse3(BigHouse):
    pass

class BigHouse4(BigHouse):
    pass


class Bush1(Tile):
    pass

class Bush2(Tile):
    pass

class Water(Tile):
    pass

class WaterRight(Tile):
    pass

class WaterLeft(Tile):
    pass

class Apartment(MultiTile):
    xdim = 1
    ydim = 2

class BigApartment(MultiTile):
    xdim = 2
    ydim = 2

class Farm(Tile):
    pass

class ShortGrass(Tile):
    pass

class Sand(Tile):
    pass

class SkyScraper(Tile):
    pass

class BSkyScraper(MultiTile):
    xdim = 2
    ydim = 1
    pass

class BSkyScraperT(MultiTile):
    xdim = 2
    ydim = 1
    pass

class BSkyScraperB(MultiTile):
    xdim = 2
    ydim = 1
    pass


class CSkyScraper(MultiTile):
    xdim = 2
    ydim = 1
    pass

class CSkyScraperT(MultiTile):
    xdim = 2
    ydim = 1
    pass

class CSkyScraperB(MultiTile):
    xdim = 2
    ydim = 1
    pass

class ParkingLot(Tile):
    pass

class BlueApartment(MultiTile):
    xdim = 2
    ydim = 4

class GiantApartment(MultiTile):
    xdim = 4
    ydim = 4

Road.touchgroup = [Road, Start, End]

class Tower(Tile):
    name = "Officer"
    text = "Just a standard cop trying to fend off the zombies"
    damage = [50, 75, 100]
    max_range = [175, 200, 225]
    fire_speed = [1.5, 1.25, 1]  # how many seconds between shots
    bullet_color = (255,255,255)
    bullet_duration = 0.1

    stun_duration = [0, 0, 0]
    splash_damage = [0, 0, 0]

    cost = [100, 50, 75] # initial tower cost, then cost of upgrades

    base_image = None
    turret_image = None
    turret_image_index = 0

    sound = "bullet"

    def __init__(self, x, y):
        super().__init__(x, y)
        self.timer = 0
        self.lvl = 0
        
        self.max_level = 99999 # placeholder value
        # accesses each attribute once to set max level to attribute with least number of upgrades to prevent errors
        self.damage
        self.fire_speed
        self.max_range

        self.info_image = load.image("officer_original.png")
        self.buy_icon = load.image("officer_head.png")
        self.locked_icon = load.image("locked_head.png")

    def update(self, deltatime):
        self.timer -= deltatime
        return self.timer < 0

    def render(self, screen, x, y, offset):
        if self.base_image != None:
            screen.blit(self.base_image, (x + offset[0], y + offset[1]))
            screen.blit(self.turret_image[self.turret_image_index], (x + 10 + offset[0], y + 10 + offset[1]))

    def fire(self, target):
        self.timer = self.fire_speed

        if target.center_pos()[0] < self.x:
            self.turret_image_index = 0
        else:
            self.turret_image_index = 1

    def render_pos(self, offset):
        return [self.x + offset[0] + SCALE / 2, self.y + offset[1] + SCALE / 2]

    def center_pos(self):
        return (self.x + SCALE / 2, self.y + SCALE / 2)

    def upgrade(self):
        if not self.is_max_level():
            self.lvl += 1

    def is_max_level(self):
        return self.lvl >= self.max_level - 1

    def upgrade_cost(self):
        if not self.is_max_level():
            return self.cost[self.lvl + 1]

    def __getattribute__(self, name):
        if name in ["damage", "max_range", "fire_speed", "stun_duration", "splash_damage"]:
            self.max_level = min(len(object.__getattribute__(self, name)), self.max_level)
            return object.__getattribute__(self, name)[self.lvl]
        else:
            return object.__getattribute__(self, name)

    def get_projectile(self, start, end):
        return BulletTrail(start, end, self.bullet_color, self.bullet_duration)

class FastTower(Tower):
    name = "Hotshot"
    text = "Takes down zombies quickly, but can only focus on what is right in front of them"
    damage = [35, 45, 50]
    fire_speed = [0.5, 0.4, 0.3]
    max_range = [110, 120, 130]
    bullet_color = (255, 0, 0)
    cost = [150, 100, 200]

    def __init__(self, x, y):
        super().__init__(x,y)
        self.info_image = load.image("redcop.png")
        self.buy_icon = load.image("redcop_head.png")

class SniperTower(Tower):
    name = "Sniper"
    text = "Loves shooting things from very far away, but takes time to aim"
    damage = [200, 300]
    fire_speed = [3, 3]
    max_range = [400, 500]
    bullet_color = (0, 0, 0)
    cost = [200, 150]

    sound = "sniper"

    def __init__(self, x, y):
        super().__init__(x,y)
        self.info_image = load.image("greycop.png")
        self.buy_icon = load.image("greycop_head.png")

class StunTower(Tower):
    name = "TASER"
    text = "Apparently tasers work on zombies. Who knew? (Upgrades increase stun duration)"
    damage = [10, 15, 20]
    fire_speed = [2, 1.75, 1.5]
    max_range = [125, 140, 160]
    stun_duration = [1, 1.25, 1.5]
    bullet_color = (0, 0, 255)
    bullet_duration = 0.5
    cost = [125, 100, 150]

    sound = "taser"

    def __init__(self, x, y):
        super().__init__(x,y)
        self.info_image = load.image("bluecop.png")
        self.buy_icon = load.image("bluecop_head.png")

class SplashTower(Tower):
    name = "Grenade"
    text = "Everyone gives them a wide bearth, but they know their explosives"
    damage = [0, 0, 0]
    fire_speed = [1, 0.9, 0.8]
    max_range = [125, 125, 125]
    cost = [200, 75, 100]
    splash_damage = [50, 75, 100]

    def get_projectile(self, start, end):
        return Grenade(start, end, self.splash_damage)

def _replace_color(surf, old, new):
    surf = surf.copy()
    for x in range(surf.get_width()):
        for y in range(surf.get_height()):
            if surf.get_at((x,y)) == old:
                surf.set_at((x,y), new)
    return surf

def ready_tiles():
    Grass.image = load.image("grass3.png").convert_alpha()
    ShortGrass.image = load.image("grass6.png").convert_alpha()
    Sand.image = load.image("sand.png").convert_alpha()
    Sidewalk.image = load.image("concrete.png").convert_alpha()
    Farm.image = load.image("farm.png").convert_alpha()
    
    ParkingLot.image = load.image("parking.png").convert_alpha()
    
    SkyScraper.image = load.image("skyscraper.png").convert_alpha()
    BSkyScraper.image = load.image("brickskyscraper.png").convert_alpha()
    BSkyScraperT.image = load.image("brickskyscraper-top.png").convert_alpha()
    BSkyScraperB.image = load.image("brickskyscraper-bottom.png").convert_alpha()
    
    CSkyScraper.image = load.image("concreteskyscraper.png").convert_alpha()
    CSkyScraperT.image = load.image("concreteskyscraper-top.png").convert_alpha()
    CSkyScraperB.image = load.image("concreteskyscraper-bottom.png").convert_alpha()
    
    BlueApartment.image = load.image("bigblueapartments.png").convert_alpha()
    GiantApartment.image = load.image("reallybigapartments.png").convert_alpha()
    #CSkyScraperB.image = load.image("concreteskyscraper-bottom.png").convert_alpha()
    
    BridgeRoad.image = load.image("bridgeroad.png").convert_alpha()
    BridgeGrate.image = load.image("bridgegrate.png").convert_alpha()
    BridgePillars.image = load.image("bridgepillars.png").convert_alpha()
    
    House.image = load.image("smallhouse.png").convert_alpha()
    HouseVariant1.image = load.image("smallhouse2.png").convert_alpha()
    BrickHouse.image = load.image("brickhouse.png").convert_alpha()
    
    BigHouse.image = load.image("garagehouse.png").convert_alpha()
    BigHouse2.image = load.image("garagehouse2.png").convert_alpha()
    BigHouse3.image = load.image("garagehouse3.png").convert_alpha()
    BigHouse4.image = load.image("garagehouse4.png").convert_alpha()
    
    Bush1.image = load.image("bush.png").convert_alpha()
    Bush2.image = load.image("bush2.png").convert_alpha()

    Tower.base_image = load.image("box.png").convert_alpha()
    officer = load.image("smofficer.png").convert_alpha()
    Tower.turret_image = [pygame.transform.flip(officer, True, False), officer]

    blue_officer = _replace_color(officer, (239,1,159), (61,61,207))
    blue_officer = _replace_color(blue_officer, (176,6,145), (19,19,133))
    StunTower.turret_image = [pygame.transform.flip(blue_officer, True, False), blue_officer]

    red_officer = _replace_color(officer, (239,1,159), (176,16,29))
    red_officer = _replace_color(red_officer, (176,6,145), (127,9,17))
    FastTower.turret_image = [pygame.transform.flip(red_officer, True, False), red_officer]

    grey_officer = load.image("smofficer_sniper.png")
    grey_officer = _replace_color(grey_officer, (239,1,159), (105,105,112))
    grey_officer = _replace_color(grey_officer, (176,6,145), (72,72,75))
    SniperTower.turret_image = [pygame.transform.flip(grey_officer, True, False), grey_officer]

    green_officer = _replace_color(officer, (239,1,159), (128,128,0))
    green_officer = _replace_color(green_officer, (176,6,145), (44,140,31))
    SplashTower.turret_image = [pygame.transform.flip(green_officer, True, False), green_officer]

    Water.image = load.image("watertilecenter.png").convert_alpha()
    WaterLeft.image = load.image("watertileleftedge.png").convert_alpha()
    WaterRight.image = load.image("watertilerightedge.png").convert_alpha()
    
    Apartment.image = load.image("apartments.png").convert_alpha()
    BigApartment.image = load.image("bigapartments.png").convert_alpha()

class TileArray():
    def __init__(self, tmap):
        self.map = tmap
        self.xdim = len(tmap)
        self.ydim = len(tmap[0])
    def __getitem__(self, tup):
        x,y = tup
        if x >= 0 and x < self.xdim and y >= 0 and y < self.ydim:
            return self.map[x][y]
        else:
            return None

# tilemap
class TileMap():
    SCALE = SCALE
    #[BigHouse, BigHouse2, BigHouse3, BigHouse4]
    colormap = {(255,0,0): [Start],
                (0,38,255): [End],
                (64,64,64): [Road],
                (255,255,255): [NoTile],
                (0, 127, 70): [House, HouseVariant1, BrickHouse],
                (0, 127, 127): [BigHouse, BigHouse2, BigHouse3, BigHouse4],
                (255, 0, 220): [Bush1, Bush2],
                (0, 255, 255): [Water],
                (0, 127, 255): [WaterLeft],
                (0, 255, 127): [WaterRight],
                (255, 216, 0): [Apartment],
                (87, 0, 127): [BigApartment],
                (0, 255, 0): [Grass],
                (255,255,0): [Sand],
                (127, 127, 127): [Sidewalk],
                (127, 127, 0): [Farm],
                (0, 127, 0): [ShortGrass],
                (20,20,20): [BridgeRoad],
                (200, 200, 200): [BridgeGrate],
                (100,100,100): [BridgePillars],
                (39, 116, 186): [SkyScraper],
                (193, 78, 40): [BSkyScraper],
                (211, 85, 43): [BSkyScraperT],
                (163, 66, 34): [BSkyScraperB],
                (210, 202, 180): [CSkyScraper],
                (222, 214, 194): [CSkyScraperT],
                (191, 184, 165): [CSkyScraperB],
                (220, 220, 220): [ParkingLot],
                (64, 61, 167): [BlueApartment],
                (226, 198, 106): [GiantApartment]
                }

    def _tile_from_color(self, color, x, y):
        if color in self.colormap:
            ret = TileMap.colormap[color]
            # pos = (x // ret[0].xdim, y // ret[0].ydim)
            # if ret[0].xdim > 1:
            #     print(x, y, pos, hash(pos))
            # choice = ret[hash(pos)%len(ret)]
            return random.choice(ret)
        print("WARNING: no tile found for color", color)
        return NoTile
    
    def __init__(self, map_surf, blocking_surf):
        self.map = []
        self.blocking = []
        self.xdim = map_surf.get_width()
        self.ydim = map_surf.get_height()
        self.starts = []

        self.build_map(self.map, map_surf)
        self.build_map(self.blocking, blocking_surf)
        
        tmap = TileArray(self.map)
        tmapblock = TileArray(self.blocking)
        
        # for x in range(self.xdim):
        #     for y in range(self.ydim):
        #         if type(self.blocking[x][y]) in (Road, Start, End):
        #             self.map[x][y] = self.blocking[x][y]
        #             self.blocking[x][y] = NoTile(x, y)
        
        for x in range(self.xdim):
            for y in range(self.ydim):
                self.map[x][y].link(tmap, x, y)
                self.blocking[x][y].link(tmapblock, x, y)

        self.selector_open = pygame.Surface((SCALE,SCALE), pygame.SRCALPHA)
        self.selector_open.fill((0,0,255))
        self.selector_open.set_alpha(128)
        self.selector_closed = pygame.Surface((SCALE,SCALE), pygame.SRCALPHA)
        self.selector_closed.fill((255,0,0))
        self.selector_closed.set_alpha(128)

    def build_map(self, map, surf):
        for x in range(self.xdim):
            row = []
            for y in range(self.ydim):
                color = surf.get_at((x,y))[0:3]
                row.append(self._tile_from_color(color, x, y)(x, y))
                if (type(row[-1]) == Start):
                    self.starts.append(row[-1])
            map.append(row)
   
    def render(self, screen, offset=[0,0]):
        self.current_offset = offset

        for x in range(self.xdim):
            for y in range(self.ydim):
                self.map[x][y].render(screen, x * SCALE, y * SCALE, offset)
        
        for x in range(self.xdim):
            for y in range(self.ydim):
                self.blocking[x][y].render(screen, x * SCALE, y * SCALE, offset)

        pygame.draw.rect(screen, (0,0,0), (offset, (self.xdim * SCALE, self.ydim * SCALE)), width=2)
    
    # def __getitem__(self, tup):
    #     x,y = tup
    #     if x >= 0 and x < self.xdim and y >= 0 and y < self.ydim:
    #         return self.map[x][y]
    #     else:
    #         return None

    # returns what tile a given screen position is in
    def screen_to_tile_coords(self, pos):
        tile = [(pos[0] - self.current_offset[0]) / SCALE, (pos[1] - self.current_offset[1]) / SCALE]

        if tile[0] >= 0 and tile[0] < self.xdim and tile[1] >= 0 and tile[1] < self.ydim:
            return [int(tile[0]), int(tile[1])]
        else:
            return False

    # returns top corner pos of tile on the screen for rendering WITHOUT OFFSET
    def tile_to_screen_coords(self, tile):
        return [tile[0] * SCALE, tile[1] * SCALE]

    def can_build(self, tile):
        return (isinstance(self.blocking[tile[0]][tile[1]], NoTile)
        and not type(self.map[tile[0]][tile[1]]) in (Road, Water, WaterRight, WaterLeft))

    # in tiles
    def get_size(self):
        return self.xdim, self.ydim

    def get_px_size(self):
        return self.xdim * SCALE, self.ydim * SCALE
        
        
   
