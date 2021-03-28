
def loadimage(path):
    pass

# Abstract class fot every thhing on the grid
class Tile(ABC):
    scale = 20
    def __init__(self, map, x, y):
        pass
    def render(self, screen, x, y):
        if (self.image):
            screen.blit(self.image, (x*self.scale, y*self.scale))

class NoTile(Tile):
    color = (255,255,255);
    image = None

class Road(Tile):
    color = (0,0,0);
    image = loadimage("images/road.png")
    def __init__(self, map, x, y):
        self.next = None

    def setnext(self, newnext, map, x, y):
        for ox,oy in [(-1,0),(0,-1),(1,0),(0,1)]:
            

class Goal(Tile):
    color = (255, 255, 0)
    def __init__(self, map, gx, gy):
        
                

class TileMap():
    tilelib = [NoTile, Road]
    def __init__(self, surf):
        self.map = []
        self.xdim = surf.get_width()
        self.ydim = surf.get_height()
        for x in range(self.xdim):
            row = []
            for y in range(self.ydim):
                color = surf.get_at((x,y))
                for tiletype in tilelib:
                    if tiletype.color == color:
                        row.append(tiletype());
            self.map.append(row);
    
    def render(self, screen):
        for x in range(self.xdim):
            for y in range(self.ydim):
                self.map[x][y].render(screen, x, y)
    
    def __getitem__(self, x, y):
        return self.map[x][y]
    
    def link(self):
        for x in range(self.xdim):
            for y in range(self.ydim):
                pass
    
        
