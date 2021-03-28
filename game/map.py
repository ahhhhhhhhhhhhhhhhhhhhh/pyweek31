import game.load as load
from abc import ABC

# Abstract class fot every thhing on the grid
class Tile(ABC):
    scale = 20
    
    def __init__(self, tilemap, x, y):
        pass
    
    def render(self, screen, x, y):
        if self.image != None:
            screen.blit(self.image, (x*self.scale, y*self.scale))

class NoTile(Tile):
    color = (255,255,255);
    image = None

class Road(Tile):
    color = (64,64,64);
    image = load.image("road.png")
    
    def __init__(self, tilemap, x, y):
        self.next = None
    
    #recursiivley sets next pointers for roads
    def setnext(self, newnext, tilemap, x, y):
        self.next = newnext
        Goal.setnext(self, newnext, tilemap, x, y)

class Goal(Tile):
    color = (255, 0, 0)
    image = load.image("goal.png")
    
    # decides path for road tiles
    def __init__(self, tilemap, gx, gy):
        for ox,oy in [(-1,0),(0,-1),(1,0),(0,1)]:
            tile = tilemap[gx+ox,gy+oy]
            if (type(tile) == Road and tile.next == None):
                tile.setnext(self, tilemap, x+ox, y+oy)
                

class TileMap():
    tilelib = [NoTile, Road, Goal]
    def __init__(self, surf):
        self.map = []
        self.xdim = surf.get_width()
        self.ydim = surf.get_height()
        for x in range(self.xdim):
            row = []
            for y in range(self.ydim):
                color = surf.get_at((x,y))
                for tiletype in self.tilelib:
                    if tiletype.color == color:
                        row.append(tiletype(self, x, y));
                        break;
                    else:
                        row.append(NoTile(self, x, y))
            self.map.append(row);
    
    def render(self, screen):
        for x in range(self.xdim):
            for y in range(self.ydim):
                self.map[x][y].render(screen, x, y)
    
    def __getitem__(self, x, y):
        return self.map[x][y]
    
        
