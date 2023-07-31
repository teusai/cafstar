from person.person import Person
import random


def randomizePerson(person, width, height):
    person.x = random.randint(person.width // 2, width - person.width // 2)
    person.y = random.randint(person.height // 2, height - person.height // 2)
    person.vx = random.randint(50, 200)
    person.vy = random.randint(50, 200)
    return person

