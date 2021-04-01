import random

import arcade

from constants import TILE_SIZE
from utils import Direction, Vector, center_of_tile


class pathcolors:
    pathcoloridx = 0
    pathcolorlist = [
        (97, 82, 103),
        (34, 61, 40),
        (57, 48, 51),
        (230, 211, 179),
        (65, 115, 76),
        (120, 101, 128),
        (230, 115, 128),
    ]

    @classmethod
    def get_color(cls):
        color = cls.pathcolorlist[cls.pathcoloridx]
        cls.pathcoloridx += 1
        return color


class Enemy(arcade.Sprite):
    def __init__(self, walls, locations, *args, **kwargs):
        super().__init__("game/assets/sprites/enemy.png", 1, *args, **kwargs)
        self._walls = walls
        self.position = locations["spawn"]
        self.waypoints = locations["waypoints"]
        self.create_full_path()
        self.pathcolor = pathcolors.get_color()
        self.movecount = 2
        self.maxvision = 3
        self.update_direction()

    @property
    def position(self) -> Vector:
        return Vector(int(self.center_x), int(self.center_y))

    @position.setter
    def position(self, pos):
        self.center_x, self.center_y = map(int, pos)

    def calculate_path(self, waypoint1, waypoint2):
        """
        Generator that yields the points between waypoint1 to waypoint2
        excludes waypoint1 from the list
        """
        pos_x, pos_y = waypoint1
        while pos_x < waypoint2[0]:
            pos_x += TILE_SIZE
            yield pos_x, pos_y
        while pos_x > waypoint2[0]:
            pos_x -= TILE_SIZE
            yield pos_x, pos_y
        while pos_y < waypoint2[1]:
            pos_y += TILE_SIZE
            yield pos_x, pos_y
        while pos_y > waypoint2[1]:
            pos_y -= TILE_SIZE
            yield pos_x, pos_y

    def create_full_path(self):
        """
        Creates a looping path through all way points
        and back to the starting position
        """
        self.path = []
        self.pathidx = 0
        for waypoint1, waypoint2 in zip(
            [self.position] + self.waypoints, self.waypoints + [self.position]
        ):
            for point in self.calculate_path(
                center_of_tile(*waypoint1), center_of_tile(*waypoint2)
            ):
                self.path.append(center_of_tile(*point))

    def move_one(self):
        """
        Moves the enemy forward one unit along his path
        """
        if self.movesleft > 0:
            self.pathidx += 1
            self.pathidx %= len(self.path)
            self.position = self.path[self.pathidx]
            self.movesleft -= 1
            self.update_vision()

    def update_direction(self):
        """
        Changes the direction the enemy is facing to face the next path location
        """
        nextposition = self.path[(self.pathidx + 1) % len(self.path)]
        basedirection = nextposition - self.position
        if basedirection[1] > 0:
            self.direction = Direction.NORTH
        elif basedirection[1] < 0:
            self.direction = Direction.SOUTH
        elif basedirection[0] > 0:
            self.direction = Direction.EAST
        elif basedirection[0] < 0:
            self.direction = Direction.WEST
        self.update_vision()

    def update_vision(self):
        self.vision_points = []
        for visiondistance in range(1, self.maxvision + 1):
            visionpoint = self.position + self.direction * visiondistance * TILE_SIZE
            if arcade.get_sprites_at_exact_point(visionpoint, self._walls):
                break
            self.vision_points.append(visionpoint)

    def update(self):
        self.movesleft = self.movecount

    def draw_path(self):
        arcade.draw_line_strip(self.path + self.path[:1], self.pathcolor, 2)

    def draw_vision(self):
        for vision_point in self.vision_points:
            arcade.draw_circle_filled(
                vision_point[0], vision_point[1], 5, arcade.color.WISTERIA, 3
            )
