import pyglet
import parseCSV
import math
import re


class Person(pyglet.sprite.Sprite):
    def __init__(self, filename, *args, **kwargs):
        img = self.__get_img(filename)
        info = self.__get_person_info(filename)
        print(info)
        super().__init__(img, *args, **kwargs)
        self.vx = 0
        self.vy = 0
        self.update(scale=0.1)

    def __get_img(self, filename):
        """Returns an image from the file filename with its anchorpoint centered"""
        img = pyglet.resource.image(filename)
        img.anchor_x = img.width // 2
        img.anchor_y = img.height // 2
        return img

    def __get_person_info(self, filename):
       """Returns a dict of info for the respective person"""
       id = int(re.search(r'\d{6}', filename).group(0))
       info = parseCSV.csvGetRow(id)
       return info

    def update(self, vx=None, vy=None, *args, **kwargs):
        self.vx = vx if vx else self.vx
        self.vy = vy if vy else self.vy
        super().update(*args, **kwargs)

    def distFromPoint(self, x, y):
        """Returns a tuple containing the signed x and y distance from a point with coordinates (x, y)"""
        return (self.x - x, self.y - y)

    def outOfBounds(self, width, height):
        """Returns wall normal vector if person sprite is completely or partially out of bounds of a box with size (width, height)"""
        if self.x + self.width // 2 > width:
            return (-1, 0)
        elif self.x - self.width // 2 < 0:
            return (1, 0)
        elif self.y + self.height // 2 > height:
            return (0, -1)
        elif self.y - self.height // 2 < 0:
            return (0, 1)
        else:
            return False

    def move(self, dt):
        """Updates the Person's coordinates based on velocity and deltatime"""
        self.update(x=self.x + self.vx * dt, y=self.y + self.vy * dt)

    def bounce(self, normal):
        """Changes the Person's velocity by reflecting based on a normal vector"""
        self.update(
            vx=self.vx + 2 * self.vx * -math.fabs(normal[0]),
            vy=self.vy + 2 * self.vy * -math.fabs(normal[1]),
        )
