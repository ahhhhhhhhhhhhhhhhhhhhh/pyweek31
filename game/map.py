from abc import ABC
import random
random.seed(10)

import pygame

import game.load as load

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

class NoTile(Tile):
    image = None

class Road(Tile):
    image = pygame.Surface((SCALE,SCALE))
    image.fill((64,64,64))
    
    def __init__(self, x, y):
        self.next = None
    
    #recursively sets next pointers for roads
    def setnext(self, newnext, tilemap, x, y):
        self.next = newnext
        End.setnext(self, tilemap, x, y)

class End(Tile):
    image = pygame.Surface((SCALE,SCALE))
    image.fill((0,38,255))
    
    # decides path for road tiles
    def link(self, tilemap, gx, gy):
        self.setnext(tilemap, gx, gy)
    
    def setnext(self, tilemap, gx, gy):
        for ox,oy in [(-1,0),(0,-1),(1,0),(0,1)]:
            tile = tilemap[gx+ox,gy+oy]
            if (type(tile) in (Road, Start) and tile.next == None):
                tile.setnext(self, tilemap, gx+ox, gy+oy)

class Start(Road):
    image = pygame.Surface((SCALE, SCALE))
    image.fill((255,0,0))
    
    def setnext(self, newnext, tilemap, x, y):
        self.next = newnext

class House(Tile):
    pass

class HouseVariant1(House):
    pass

def ready_tiles():
    House.image = load.image("smallhouse50.png").convert_alpha()
    HouseVariant1.image = load.image("smallhouse50variant.png").convert_alpha()

class NoBlocking(Tile):
    def render(self, screen, x, y):
        pass

class Tower(Tile):
    image = pygame.Surface((10, 10))
    image.fill((255,0,0))

class TileMap():
    colormap = {(255,0,0): [Start],
                (0,38,255): [End],
                (64,64,64): [Road],
                (255,255,255): [NoTile],
                (0, 127, 70): [House, HouseVariant1]}

    def _tile_from_color(self, color):
        ret = TileMap.colormap[color]
        return random.choice(ret)
    
    def __init__(self, map_surf, blocking_surf):
        self.map = []
        self.blocking = []
        self.xdim = map_surf.get_width()
        self.ydim = map_surf.get_height()
        self.starts = []

        self.build_map(self.map, map_surf, NoTile)
        self.build_map(self.blocking, blocking_surf, NoBlocking)
        
        for x in range(self.xdim):
            for y in range(self.ydim):
                self.map[x][y].link(self, x, y)

        self.selector_open = pygame.Surface((SCALE,SCALE), pygame.SRCALPHA)
        self.selector_open.fill((0,0,255))
        self.selector_open.set_alpha(128)
        self.selector_closed = pygame.Surface((SCALE,SCALE), pygame.SRCALPHA)
        self.selector_closed.fill((255,0,0))
        self.selector_closed.set_alpha(128)

    def build_map(self, map, surf, default_tile):
        for x in range(self.xdim):
            row = []
            for y in range(self.ydim):
                color = surf.get_at((x,y))[0:3]
                if color in self.colormap:
                    row.append(self._tile_from_color(color)(x, y))
                    if (type(row[-1]) == Start): self.starts.append(row[-1])
                else:
                    print(f"warning, no tile conversion for color={color}")
                    row.append(default_tile(x, y))
            map.append(row)
   
    def render(self, screen, offset=[0,0]):
        self.current_offset = offset

        for x in range(self.xdim):
            for y in range(self.ydim):
                coords = self.tile_to_screen_coords([x,y])
                self.map[x][y].render(screen, coords[0], coords[1])
                self.blocking[x][y].render(screen, coords[0], coords[1])

        selected_tile = self.screen_to_tile_coords(pygame.mouse.get_pos())
        if selected_tile:
            coords = self.tile_to_screen_coords(selected_tile)
            canbuild = self.can_build(selected_tile)

            if canbuild:
                screen.blit(self.selector_open, coords)
            else:
                screen.blit(self.selector_closed, coords)
            
            for event in TileMap.loop.get_events():
                if event.type == pygame.MOUSEBUTTONDOWN and not getattr(event, "used", False) and event.button == 1:
                    event.used = True
                    
                    if canbuild:  
                        print("building tower", selected_tile)
                        self.blocking[selected_tile[0]][selected_tile[1]] = Tower(coords[0], coords[1])
    
    def __getitem__(self, tup):
        x,y = tup
        if x >= 0 and x < self.xdim and y >= 0 and y < self.ydim:
            return self.map[x][y]
        else:
            return None

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
        return isinstance(self.blocking[tile[0]][tile[1]], NoBlocking) and not isinstance(self.map[tile[0]][tile[1]], Road)
   
