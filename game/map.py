from abc import ABC

import pygame

import game.load as load

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
    image = pygame.Surface((40,40))
    image.fill((255,255,255))

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
    image.fill((255,0,0))
    
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
    image.fill((0,255,0))
    
    def setnext(self, newnext, tilemap, x, y):
        self.next = newnext

class TileMap():
    SCALE = 40
    colormap = {(255,0,0): Start,
                (0,38,255): End,
                (64,64,64): Road,
                (255,255,255): NoTile}
    
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
            self.map.append(row);
        
        for x in range(self.xdim):
            for y in range(self.ydim):
                self.map[x][y].link(self, x, y)
   
    def render(self, screen, offset=[0,0]):
        for x in range(self.xdim):
            for y in range(self.ydim):
                self.map[x][y].render(screen, offset[0]+x*TileMap.SCALE, offset[1]+y*TileMap.SCALE)
    
    def __getitem__(self, tup):
        x,y = tup
        if x >= 0 and x < self.xdim and y >= 0 and y < self.ydim:
            return self.map[x][y]
        else:
            return None
        
