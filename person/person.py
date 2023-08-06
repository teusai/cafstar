import pyglet
import math
import random
import re


class Person():
    def __init__(self, index, info, *args, **kwargs):
        self.index = index
        self.info = info
        self.category = int(info['Category ID'])
        
        self.x = 0
        self.y = 0
        self.vx = 0
        self.vy = 0
        
        self.rotation = 0
        self.rotSpeed = random.uniform(10.0, 60.0) * (-1 if random.randint(0, 1) == 1 else 1)
        
        self.scale = random.randint(16, 24) / 100.0
        self.opacity = 255.
        
        self.timeLimit = 10
        self.timeUp = False
        self.caught = False
        self.pauseTime = 3
        self.handler = None
    
    def setHandler(self, handler):
        self.handler = handler

    def update(self, vx=None, vy=None, *args, **kwargs):
        self.vx = vx if vx else self.vx
        self.vy = vy if vy else self.vy

    def distFromPoint(self, x, y):
        return math.sqrt((self.x - x)*(self.x - x) + (self.y - y)*(self.y - y))

    # def outOfBounds(self, width, height):
    #     """Returns wall normal vector if person sprite is completely or partially out of bounds of a box with size (width, height)"""
    #     if self.x + self.width // 2 > width:
    #         return (-1, 0)
    #     elif self.x - self.width // 2 < 0:
    #         return (1, 0)
    #     elif self.y + self.height // 2 > height:
    #         return (0, -1)
    #     elif self.y - self.height // 2 < 0:
    #         return (0, 1)
    #     else:
    #         return False

    def step(self, dt):
        """Updates the Person's coordinates based on velocity and deltatime"""
        if self.caught:
            self.pause(dt)
            return
        if self.timeUp:
            self.fadeout(dt)
            return
        
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.rotation += self.rotSpeed * dt

        self.timeLimit -= dt
        self.timeUp = self.timeLimit <= 0

    def pause(self, dt):
        """Sub-function of step for waiting afte the person is caught to fadeout"""
        if self.pauseTime <= 0:
            self.fadeout(dt)
            return
        self.pauseTime -= dt

    def fadeout(self, dt):
        """Sub-function of self.step that handles fading out before despawing"""
        if self.opacity < 0.01:
            self.despawn()
            return
        self.opacity *= (1 - dt) * 0.95

    # def bounce(self, normal):
    #     """Changes the Person's velocity by reflecting based on a normal vector"""
    #     self.update(
    #         vx=self.vx + 2 * self.vx * -math.fabs(normal[0]),
    #         vy=self.vy + 2 * self.vy * -math.fabs(normal[1]),
    #     )

    def despawn(self):
        if self.handler:
            self.handler.remove(self)
        del self

    def __repr__(self):
        return f"Person {self.info['ID']}: {self.info['First Name']} {self.info['Last Name']}, Category {self.category}"