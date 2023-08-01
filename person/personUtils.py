from person.person import Person
import random
import math


def randomizePerson(person, width, height):
    return randomizeFromCenter(person, width, height)

    person.x = random.randint(person.width // 2, width - person.width // 2)
    person.y = random.randint(person.height // 2, height - person.height // 2)
    person.vx = random.randint(50, 200)
    person.vy = random.randint(50, 200)
    return person

def randomizeFromCenter(person, width, height):
    person.x = width // 2
    person.y = height // 2
    speed = random.uniform(100.0, 150.0)         # change speed of people
    angle = random.uniform(0.0, 2*math.pi)
    person.vx = speed * math.cos(angle)
    person.vy = speed * math.sin(angle)
    return person