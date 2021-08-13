from abc import ABC
import random

random.seed(10)

import pygame
import pygame._sdl2.video as video

import game.load as load
import game.utils as utils

SCALE = 50

# Abstract class fot every thing on the grid
class Tile(ABC):
    xdim = 1
    ydim = 1
    # passes in x and y pos
    def __init__(self, x, y):
        self.x, self.y = x, y

    # renders at screen pos (Not tile grid pos)
    def render(self, x, y, offset):
        if self.image != None:
            self.image.draw(None, (x + offset[0], y + offset[1]))

    # stuff that needs to happen after map creation
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
        while type(tilemap[x - distx - 1, y]) == type(self):
            distx += 1

        disty = 0
        while type(tilemap[x, y - disty - 1]) == type(self):
            disty += 1

        if distx % self.xdim == 0 and disty % self.ydim == 0:
            self.corner = True
            for ox in range(self.xdim):
                for oy in range(self.ydim):
                    if type(tilemap[self.x + ox, self.y + oy]) != type(self):
                        tilemap.map[self.x + ox][self.y + oy] = type(self)(
                            self.x + ox, self.y + oy
                        )

    def render(self, x, y, offset):
        if self.corner:
            super().render(x, y, offset)


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
        for ox, oy in [(1, 0), (0, -1), (-1, 0), (0, 1)]:
            tile = tilemap[gx + ox, gy + oy]
            issame = (not self.touchgroup and type(tile) == type(self)) or type(
                tile
            ) in self.touchgroup
            dirs.append("1" if issame else "0")

        for rot in range(4):
            strdir = "".join(dirs[rot:]) + "".join(dirs[:rot])

            num = int(strdir[::-1], 2)
            if num in (1, 3, 5, 7, 15):
                img = self.images[(1, 3, 5, 7, 15).index(num)]
                # self.image = pygame.transform.rotate(img, 90*rot)
                self.image = video.Image(img)
                self.image.angle = -90 * rot
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

    def __init__(self, x, y):
        super().__init__(x, y)
        self.next = {}

    # recursively sets next pointers for roads
    def setnext(self, newnext, tilemap, endgoal, dist, x, y):
        self.next[endgoal] = (newnext, dist)
        End.setnext(self, tilemap, endgoal, dist, x, y)


class End(Tile):
    # decides path for road tiles
    def link(self, tilemap, gx, gy):
        self.setnext(tilemap, self, 0, gx, gy)

    def setnext(self, tilemap, endgoal, dist, gx, gy):
        for ox, oy in [(-1, 0), (0, -1), (1, 0), (0, 1)]:
            tile = tilemap[gx + ox, gy + oy]
            if type(tile) in (Road, Start) and endgoal not in tile.next:
                tile.setnext(self, tilemap, endgoal, dist + 1, gx + ox, gy + oy)


class Start(Road):
    # image = pygame.Surface((SCALE, SCALE))
    # image.fill((255,0,0))
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
    bullet_color = (255, 255, 255)
    bullet_duration = 0.1

    cost = [100, 50, 75]  # initial tower cost, then cost of upgrades

    base_image = None
    turret_image = None
    turret_image_index = 0

    def __init__(self, x, y):
        super().__init__(x, y)
        self.timer = 0
        self.lvl = 0

        self.max_level = 99999  # placeholder value
        # accesses each attribute once to set max level to attribute with least number of upgrades to prevent errors
        self.damage
        self.fire_speed
        self.max_range

        self.info_image = load.surface("officer_original.png")
        self.buy_icon = load.surface("officer_head.png")
        self.locked_icon = load.surface("locked_head.png")

    def update(self, deltatime):
        self.timer -= deltatime
        return self.timer < 0

    def render(self, x, y, offset):
        if self.base_image != None:
            self.base_image.draw(None, (x + offset[0], y + offset[1]))
            # screen.blit(self.base_image, (x + offset[0], y + offset[1]))
            # screen.blit(self.turret_image[self.turret_image_index], (x + 10 + offset[0], y + 10 + offset[1]))
            self.turret_image[self.turret_image_index].draw(
                None, (x + 10 + offset[0], y + 10 + offset[1])
            )

    def fire(self, target):
        self.timer = self.fire_speed

        if target.center_pos()[0] < self.x:
            self.turret_image_index = 0
        else:
            self.turret_image_index = 1

    def center_pos(self, offset):
        return [self.x + offset[0] + SCALE / 2, self.y + offset[1] + SCALE / 2]

    def upgrade(self):
        if not self.is_max_level():
            self.lvl += 1

    def is_max_level(self):
        return self.lvl >= self.max_level - 1

    def upgrade_cost(self):
        if not self.is_max_level():
            return self.cost[self.lvl + 1]

    def __getattribute__(self, name):
        if name in ["damage", "max_range", "fire_speed", "stun_duration"]:
            self.max_level = min(
                len(object.__getattribute__(self, name)), self.max_level
            )
            return object.__getattribute__(self, name)[self.lvl]
        else:
            return object.__getattribute__(self, name)


class FastTower(Tower):
    name = "Hotshot"
    text = "Takes down zombies quickly, but can only focus on what is right in front of them"
    damage = [35, 45, 50]
    fire_speed = [0.5, 0.4, 0.3]
    max_range = [110, 120, 130]
    bullet_color = (255, 0, 0)
    cost = [150, 100, 200]

    def __init__(self, x, y):
        super().__init__(x, y)
        self.info_image = load.surface("redcop.png")
        self.buy_icon = load.surface("redcop_head.png")


class SniperTower(Tower):
    name = "Sniper"
    text = "Loves shooting things from very far away, but takes time to aim"
    damage = [200, 300]
    fire_speed = [3, 3]
    max_range = [400, 500]
    bullet_color = (0, 0, 0)
    cost = [200, 150]

    def __init__(self, x, y):
        super().__init__(x, y)
        self.info_image = load.surface("greycop.png")
        self.buy_icon = load.surface("greycop_head.png")


class StunTower(Tower):
    name = "TASER"
    text = (
        "Apparently tasers work on zombies. Who knew? (Upgrades increase stun duration)"
    )
    damage = [10, 15, 20]
    fire_speed = [2, 1.75, 1.5]
    max_range = [125, 140, 160]
    stun_duration = [1, 1.25, 1.5]
    bullet_color = (0, 0, 255)
    bullet_duration = 0.5
    cost = [125, 100, 150]

    def __init__(self, x, y):
        super().__init__(x, y)
        self.info_image = load.surface("bluecop.png")
        self.buy_icon = load.surface("bluecop_head.png")


def _replace_color(surf, old, new):
    surf = surf.copy()
    for x in range(surf.get_width()):
        for y in range(surf.get_height()):
            if surf.get_at((x, y)) == old:
                surf.set_at((x, y), new)
    return surf


def ready_tiles():
    Grass.image = load.image("grass3.png")
    ShortGrass.image = load.image("grass6.png")
    Sand.image = load.image("sand.png")
    Sidewalk.image = load.image("concrete.png")
    Farm.image = load.image("farm.png")

    ParkingLot.image = load.image("parking.png")

    SkyScraper.image = load.image("skyscraper.png")
    BSkyScraper.image = load.image("brickskyscraper.png")
    BSkyScraperT.image = load.image("brickskyscraper-top.png")
    BSkyScraperB.image = load.image("brickskyscraper-bottom.png")

    CSkyScraper.image = load.image("concreteskyscraper.png")
    CSkyScraperT.image = load.image("concreteskyscraper-top.png")
    CSkyScraperB.image = load.image("concreteskyscraper-bottom.png")

    BlueApartment.image = load.image("bigblueapartments.png")
    GiantApartment.image = load.image("reallybigapartments.png")

    BridgeRoad.image = load.image("bridgeroad.png")
    BridgeGrate.image = load.image("bridgegrate.png")
    BridgePillars.image = load.image("bridgepillars.png")

    House.image = load.image("smallhouse.png")
    HouseVariant1.image = load.image("smallhouse2.png")
    BrickHouse.image = load.image("brickhouse.png")

    BigHouse.image = load.image("garagehouse.png")
    BigHouse2.image = load.image("garagehouse2.png")
    BigHouse3.image = load.image("garagehouse3.png")
    BigHouse4.image = load.image("garagehouse4.png")

    Bush1.image = load.image("bush.png")
    Bush2.image = load.image("bush2.png")

    Tower.base_image = load.image("box.png")
    officer = load.surface("smofficer.png")
    officer_tex = video.Texture.from_surface(load.RENDERER, officer)
    Tower.turret_image = [video.Image(officer_tex), video.Image(officer_tex)]
    Tower.turret_image[0].flipX = True

    blue_officer = _replace_color(officer, (239, 1, 159), (61, 61, 207))
    blue_officer = _replace_color(blue_officer, (176, 6, 145), (19, 19, 133))
    blue_officer_tex = video.Texture.from_surface(load.RENDERER, blue_officer)
    StunTower.turret_image = [
        video.Image(blue_officer_tex),
        video.Image(blue_officer_tex),
    ]
    StunTower.turret_image[0].flipX = True

    red_officer = _replace_color(officer, (239, 1, 159), (176, 16, 29))
    red_officer = _replace_color(red_officer, (176, 6, 145), (127, 9, 17))
    red_officer_tex = video.Texture.from_surface(load.RENDERER, red_officer)
    FastTower.turret_image = [
        video.Image(red_officer_tex),
        video.Image(red_officer_tex),
    ]
    FastTower.turret_image[0].flipX = True

    grey_officer = load.surface("smofficer_sniper.png")
    grey_officer = _replace_color(grey_officer, (239, 1, 159), (105, 105, 112))
    grey_officer = _replace_color(grey_officer, (176, 6, 145), (72, 72, 75))
    grey_officer_tex = video.Texture.from_surface(load.RENDERER, grey_officer)
    SniperTower.turret_image = [
        video.Image(grey_officer_tex),
        video.Image(grey_officer_tex),
    ]
    SniperTower.turret_image[0].flipX = True

    Water.image = load.image("watertilecenter.png")
    WaterLeft.image = load.image("watertileleftedge.png")
    WaterRight.image = load.image("watertilerightedge.png")

    Apartment.image = load.image("apartments.png")
    BigApartment.image = load.image("bigapartments.png")

    Road.images = [
        load.image("road01.png"),
        load.image("road03.png"),
        load.image("road05.png"),
        load.image("road07.png"),
        load.image("road15.png"),
    ]

    Start.image = pygame.Surface((SCALE, SCALE))
    Start.image.fill((255, 0, 0))
    Start.image = video.Texture.from_surface(load.RENDERER, Start.image)

    End.image = pygame.Surface((SCALE, SCALE))
    End.image.fill((0, 38, 255))
    End.image = video.Texture.from_surface(load.RENDERER, End.image)


class TileArray:
    def __init__(self, tmap):
        self.map = tmap
        self.xdim = len(tmap)
        self.ydim = len(tmap[0])

    def __getitem__(self, tup):
        x, y = tup
        if x >= 0 and x < self.xdim and y >= 0 and y < self.ydim:
            return self.map[x][y]
        else:
            return None


# tilemap
class TileMap:
    SCALE = SCALE
    # [BigHouse, BigHouse2, BigHouse3, BigHouse4]
    colormap = {
        (255, 0, 0): [Start],
        (0, 38, 255): [End],
        (64, 64, 64): [Road],
        (255, 255, 255): [NoTile],
        (0, 127, 70): [House, HouseVariant1, BrickHouse],
        (0, 127, 127): [BigHouse, BigHouse2, BigHouse3, BigHouse4],
        (255, 0, 220): [Bush1, Bush2],
        (0, 255, 255): [Water],
        (0, 127, 255): [WaterLeft],
        (0, 255, 127): [WaterRight],
        (255, 216, 0): [Apartment],
        (87, 0, 127): [BigApartment],
        (0, 255, 0): [Grass],
        (255, 255, 0): [Sand],
        (127, 127, 127): [Sidewalk],
        (127, 127, 0): [Farm],
        (0, 127, 0): [ShortGrass],
        (20, 20, 20): [BridgeRoad],
        (200, 200, 200): [BridgeGrate],
        (100, 100, 100): [BridgePillars],
        (39, 116, 186): [SkyScraper],
        (193, 78, 40): [BSkyScraper],
        (211, 85, 43): [BSkyScraperT],
        (163, 66, 34): [BSkyScraperB],
        (210, 202, 180): [CSkyScraper],
        (222, 214, 194): [CSkyScraperT],
        (191, 184, 165): [CSkyScraperB],
        (220, 220, 220): [ParkingLot],
        (64, 61, 167): [BlueApartment],
        (226, 198, 106): [GiantApartment],
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
        self.xdim = map_surf.get_rect().w
        self.ydim = map_surf.get_rect().h
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

        self.selector_open = pygame.Surface((SCALE, SCALE))
        self.selector_open.fill((0, 0, 255))
        self.selector_open.set_alpha(128)
        n = pygame.Surface((SCALE, SCALE), pygame.SRCALPHA)
        n.blit(self.selector_open, (0, 0))
        self.selector_open = video.Texture.from_surface(load.RENDERER, n)

        self.selector_closed = pygame.Surface((SCALE, SCALE), pygame.SRCALPHA)
        self.selector_closed.fill((255, 0, 0))
        self.selector_closed.set_alpha(128)
        n = pygame.Surface((SCALE, SCALE), pygame.SRCALPHA)
        n.blit(self.selector_closed, (0, 0))
        self.selector_closed = video.Texture.from_surface(load.RENDERER, n)

    def build_map(self, map, surf):
        for x in range(self.xdim):
            row = []
            for y in range(self.ydim):
                color = surf.get_at((x, y))[0:3]
                row.append(self._tile_from_color(color, x, y)(x, y))
                if type(row[-1]) == Start:
                    self.starts.append(row[-1])
            map.append(row)

    def render(self, renderer, offset=[0, 0]):
        self.current_offset = offset

        for x in range(self.xdim):
            for y in range(self.ydim):
                self.map[x][y].render(x * SCALE, y * SCALE, offset)

        for x in range(self.xdim):
            for y in range(self.ydim):
                self.blocking[x][y].render(x * SCALE, y * SCALE, offset)

        renderer.draw_color = pygame.Color("black")
        renderer.draw_rect((offset, (self.xdim * SCALE, self.ydim * SCALE)))

        # pygame.draw.rect(screen, (0,0,0), (offset, (self.xdim * SCALE, self.ydim * SCALE)), width=2)

    # def __getitem__(self, tup):
    #     x,y = tup
    #     if x >= 0 and x < self.xdim and y >= 0 and y < self.ydim:
    #         return self.map[x][y]
    #     else:
    #         return None

    # returns what tile a given screen position is in
    def screen_to_tile_coords(self, pos):
        tile = [
            (pos[0] - self.current_offset[0]) / SCALE,
            (pos[1] - self.current_offset[1]) / SCALE,
        ]

        if (
            tile[0] >= 0
            and tile[0] < self.xdim
            and tile[1] >= 0
            and tile[1] < self.ydim
        ):
            return [int(tile[0]), int(tile[1])]
        else:
            return False

    # returns top corner pos of tile on the screen for rendering WITHOUT OFFSET
    def tile_to_screen_coords(self, tile):
        return [tile[0] * SCALE, tile[1] * SCALE]

    def can_build(self, tile):
        return isinstance(self.blocking[tile[0]][tile[1]], NoTile) and not type(
            self.map[tile[0]][tile[1]]
        ) in (Road, Water, WaterRight, WaterLeft)

    # in tiles
    def get_size(self):
        return self.xdim, self.ydim

    def get_px_size(self):
        return self.xdim * SCALE, self.ydim * SCALE
