import pyglet
import glob
import random
from Person import Person
from constants import FRAMERATE, WIDTH, HEIGHT

people_path = "assets/people/"
people_image_paths = [f for f in glob.glob(people_path + "*-transparent.png")]
num_imgs = len(people_image_paths)

window = pyglet.window.Window(width=WIDTH, height=HEIGHT)
pyglet.gl.glClearColor(0.3, 0.3, 0.3, 1)


def load_rand_person():
    index = random.randint(0, num_imgs - 1)
    return Person(people_image_paths[index])


def randomize_person(person):
    person.x = random.randint(person.width // 2, WIDTH - person.width // 2)
    person.y = random.randint(person.height // 2, HEIGHT - person.height // 2)
    person.vx = random.randint(50, 200)
    person.vy = random.randint(50, 200)
    return person


def update_person(person, dt):
    person.move(dt)
    person.draw()
    bounding = person.outOfBounds(WIDTH, HEIGHT)
    if bounding:
        if person.vx * bounding[0] < 0 or person.vy * bounding[1] < 0:
            person.bounce(bounding)


people = [randomize_person(load_rand_person()) for i in range(10)]


def game_loop(dt):
    window.clear()

    for person in people:
        update_person(person, dt)


pyglet.clock.schedule_interval(game_loop, FRAMERATE)
pyglet.app.run(FRAMERATE)
