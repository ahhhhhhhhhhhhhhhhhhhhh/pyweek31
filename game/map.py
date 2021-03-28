

class Tile(ABC):
    def __init__(self, x, y):
        pass
    def render(self):
        self.image
        pass

class NoTile(Tile):
    color = (255,255,255);

class Road(Tile):
    color = (0,0,0);
    def __init__(self):
        self.next = None

class TileMap():
    tilelib = [NoTile, Road]
    def __init__(self, surf):
        self.map = []
        for x in range(surf.get_width()):
            row = []
            for y in range(surf.get_height()):
                color = surf.get_at((x,y))
                for tiletype in tilelib:
                    if tiletype.color == color:
                        row.append(tiletype());
            self.map.append(row);
    
    def render(self):
        pass
