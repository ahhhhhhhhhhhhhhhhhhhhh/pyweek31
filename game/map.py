from abc import ABC
import random
random.seed(10)

import pygame

import game.load as load
import game.utils as utils

SCALE = 50

# Abstract class fot every thing on the grid
class Tile(ABC):
    #passes in x and y pos
    def __init__(self, x, y):
        self.x, self.y = x, y
    
    #renders at screen pos (Not tile grid pos)
    def render(self, screen, x, y):
        if self.image != None:
            screen.blit(self.image, (x, y))
    
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
        while type(tilemap[x+distx, y]) == type(self):
            distx += 1
        
        disty = 0
        while type(tilemap[x, y+disty]) == type(self):
            disty += 1
        
        if distx%self.xdim == 0 and disty%self.ydim == 0:
            self.corner = True
    
    def render(self, screen, x, y):
        if self.corner:
            super().render(screen, x, y)

class NoTile(Tile):
    image = None

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

class BigHouse(MultiTile):
    xdim = 2
    ydim = 2

class HouseVariant1(House):
    pass

class BrickHouse(House):
    pass

Road.touchgroup = [Road, Start, End]

class Tower(Tile):
    name = "Officer"
    damage = 50
    max_range = 175
    fire_speed = 2  # how many seconds between shots
    bullet_color = (255,255,255)

    timer = 0

    base_image = None
    turret_image = None
    turret_image_index = 0

    def __init__(self, x, y):
        super().__init__(x, y)
        self.button = utils.ToggleButton([0,0,SCALE,SCALE])

    def update(self, deltatime):
        self.timer -= deltatime
        return self.timer < 0

    # overloaded because the button needs to know the location
    def render(self, screen, x, y):
        if self.button.active:
            tower_pos = self.center_pos()
            pygame.draw.circle(screen, (255,255,255), tower_pos, self.max_range, width=1)
    
        if self.base_image != None:
            screen.blit(self.base_image, (x, y))
            screen.blit(self.turret_image[self.turret_image_index], (x, y - 10))
        self.button.update_location((x, y))
        self.button.draw(screen)

    def fire(self, target):
        self.timer = self.fire_speed

        if target.center_pos()[0] < self.x:
            self.turret_image_index = 0
        else:
            self.turret_image_index = 1

    def center_pos(self):
        return [self.x + SCALE / 2, self.y + SCALE / 2]

class FastTower(Tower):
    name = "Fast Officer"
    damage = 35
    fire_speed = 0.5
    max_range = 120
    bullet_color = (255, 0, 0)

def ready_tiles():
    House.image = load.image("smallhouse50.png").convert_alpha()
    HouseVariant1.image = load.image("smallhouse50variant.png").convert_alpha()
    BrickHouse.image = load.image("brickhouse.png").convert_alpha()
    BigHouse.image = load.image("garagehouse.png").convert_alpha()
    Tower.base_image = load.image("box.png").convert_alpha()
    Tower.turret_image = [load.image("smallofficerL.png").convert_alpha(), load.image("smallofficerR.png").convert_alpha()]


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
    


class TileMap():
    colormap = {(255,0,0): [Start],
                (0,38,255): [End],
                (64,64,64): [Road],
                (255,255,255): [NoTile],
                (0, 127, 70): [House, HouseVariant1, BrickHouse],
                (0, 127, 127): [BigHouse]}

    def _tile_from_color(self, color):
        if color in self.colormap:
            ret = TileMap.colormap[color]
            return random.choice(ret)
        return NoTile
    
    def __init__(self, map_surf, blocking_surf):
        self.map = []
        self.blocking = []
        self.xdim = map_surf.get_width()
        self.ydim = map_surf.get_height()
        self.starts = []

        self.build_map(self.map, map_surf)
        self.build_map(self.blocking, blocking_surf)
        
        for x in range(self.xdim):
            for y in range(self.ydim):
                self.map[x][y].link(TileArray(self.map), x, y)
                self.blocking[x][y].link(TileArray(self.blocking), x, y)

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
                row.append(self._tile_from_color(color)(x, y))
                if (type(row[-1]) == Start):
                    self.starts.append(row[-1])
            map.append(row)
   
    def render(self, screen, offset=[0,0]):
        self.current_offset = offset

        for x in range(self.xdim):
            for y in range(self.ydim):
                coords = self.tile_to_screen_coords([x,y])
                self.map[x][y].render(screen, coords[0], coords[1])
                self.blocking[x][y].render(screen, coords[0], coords[1])
    
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

    # returns top corner pos of tile on the screen for rendering
    def tile_to_screen_coords(self, tile):
        return [self.current_offset[0] + tile[0] * SCALE, self.current_offset[1] + tile[1] * SCALE]

    def can_build(self, tile):
        return isinstance(self.blocking[tile[0]][tile[1]], NoTile) and not isinstance(self.map[tile[0]][tile[1]], Road)
   
