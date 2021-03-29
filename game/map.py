from abc import ABC

import pygame

import game.load as load

SCALE = 40

# Abstract class fot every thing on the grid
class Tile(ABC):
    #passes in x and y pos
    def __init__(self, x, y):
        pass
    
    #renders at screen pos (Not tile grid pos)
    def render(self, screen, x, y):
        if self.image != None:
            screen.blit(self.image, (x, y))
    
    #stuff that needs to happen after map creation
    def link(self, tilemap, x, y):
        pass

class NoTile(Tile):
    image = None
    #image = pygame.Surface((40,40))
    #image.fill((255,255,255))

class Road(Tile):
    image = pygame.Surface((40,40))
    image.fill((64,64,64))
    
    def __init__(self, x, y):
        self.next = None
    
    #recursively sets next pointers for roads
    def setnext(self, newnext, tilemap, x, y):
        self.next = newnext
        End.setnext(self, tilemap, x, y)

class End(Tile):
    image = pygame.Surface((40,40))
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
    image = pygame.Surface((40, 40))
    image.fill((255,0,0))
    
    def setnext(self, newnext, tilemap, x, y):
        self.next = newnext

class House(Tile):
    pass

def ready_tiles():
    House.image = load.image("smallhouse.png")
    House.image = pygame.transform.scale(House.image, (SCALE, SCALE))
    House.image = House.image.convert_alpha()

class NoBlocking(Tile):
    def render(self, screen, x, y):
        pass

class Tower(Tile):
    image = pygame.Surface((10, 10))
    image.fill((255,0,0))

class TileMap():
    colormap = {(255,0,0): Start,
                (0,38,255): End,
                (64,64,64): Road,
                (255,255,255): NoTile,
                (0, 127, 70): House}
    
    def __init__(self, surf):
        self.map = []
        self.xdim = surf.get_width()
        self.ydim = surf.get_height()
        self.starts = []

        for x in range(self.xdim):
            row = []
            for y in range(self.ydim):
                color = surf.get_at((x,y))[0:3]
                if color in self.colormap:
                    row.append(TileMap.colormap[color](x, y))
                    if (type(row[-1]) == Start): self.starts.append(row[-1])
                else:
                    print(f"warning, no tile conversion for color={color}")
                    row.append(NoTile(x, y))
            self.map.append(row)

        self.blocking = [[NoBlocking(x,y) for y in range(self.ydim)] for x in range(self.xdim)]
        
        for x in range(self.xdim):
            for y in range(self.ydim):
                self.map[x][y].link(self, x, y)
   
    def render(self, screen, offset=[0,0]):
        self.current_offset = offset

        for x in range(self.xdim):
            for y in range(self.ydim):
                coords = self.tile_to_screen_coords([x,y])
                self.map[x][y].render(screen, coords[0], coords[1])
                self.blocking[x][y].render(screen, coords[0], coords[1])
    
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

        
