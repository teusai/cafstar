import pyglet
import random
import glob
from person.person import Person
from person.catchPeople import catchPeople
from person.personUtils import randomizePerson
from utils.readConfig import readConfig
from utils.readInfo import readInfo
from utils.readCategories import readCategories
from utils.drawScoreboard import drawScoreboard
from utils.drawEndScreen import drawEndScreen

import gc

config = readConfig('cafstar.cfg')
peopleInfo = readInfo('assets/people-info-id-ordered.csv')
categories = readCategories('assets/categories.csv')
peopleImageURLS = sorted(glob.glob('assets/people/*.png'))
numTotalPeople = len(peopleImageURLS)
print(peopleImageURLS)
backgroundImage = pyglet.resource.image('assets/' + config['backgroundfilename'])



window = pyglet.window.Window(width=config['windowwidth'], height=config['windowheight'])
pyglet.gl.glClearColor(0.3, 0.3, 0.3, 1)

catcher = pyglet.shapes.Circle(0, 0, radius=90)

@window.event
def on_mouse_motion(x, y, dx, dy):
    global catcher
    catcher.x = x
    catcher.y = y


activePeople = []
usedPeople = set()
peopleBatch = pyglet.graphics.Batch()
highScore = 0
currentScore = 0
activeCategory = 1
catchAreas = [pyglet.shapes.Circle(x=400, y=300, radius=100), catcher]
remainingTime = config['gametimelimit']


def gameReset(dt):
    pyglet.clock.unschedule(gameWait)
    global activePeople, usedPeople, currentScore, remainingTime, peopleBatch
    for p in activePeople:
        p.despawn()
    del activePeople
    del usedPeople
    del peopleBatch
    activePeople = []
    usedPeople = set()
    peopleBatch = pyglet.graphics.Batch()
    currentScore = 0
    remainingTime = config['gametimelimit']

    print(gc.get_count())
    gc.collect()
    print(gc.get_count())

    pickActiveCategory()

    pyglet.clock.schedule_interval(gameLoop, config['framerate'])
    pyglet.clock.schedule_interval(spawnPerson, config['personspawnrate'])
    pyglet.clock.schedule_once(gameEnd, config['gametimelimit'])


def gameLoop(dt):
    global remainingTime, currentScore

    if remainingTime < 0:
        print("game ended")
        return

    # print("game looping")
    # backgroundImage.blit(0, 0)
    window.clear()
    for area in catchAreas:
        area.draw()
    drawScoreboard(config['windowwidth'], config['windowheight'], config['tabletowindowratio'], currentScore, remainingTime, categories[activeCategory-1])
    peopleBatch.draw()

    caughtPeople = catchPeople(activePeople, catchAreas)
    if caughtPeople:
        print(caughtPeople)
        for p in caughtPeople:
            p.timeLimit = 0
            p.catchable = False
            if p.category == activeCategory:
                currentScore += 1
                pickActiveCategory()


    for person in activePeople:
        bounding = person.outOfBounds(config['windowwidth'], config['windowheight'])
        if bounding:
            if person.vx * bounding[0] < 0 or person.vy * bounding[1] < 0:
                person.bounce(bounding)
        person.step(dt)
    
    
    remainingTime -= dt


def gameEnd(dt):
    pyglet.clock.unschedule(gameLoop)
    pyglet.clock.unschedule(spawnPerson)
    global remainingTime
    remainingTime = config['gamewaittime']
    pyglet.clock.schedule_interval(gameWait, config['framerate'])
    pyglet.clock.schedule_once(gameReset, config['gamewaittime'])

def gameWait(dt):
    global remainingTime
    # backgroundImage.blit(0,0)
    window.clear()
    drawScoreboard(config['windowwidth'], config['windowheight'], config['tabletowindowratio'], currentScore, remainingTime, categories[activeCategory-1])
    remainingTime -= dt


def spawnPerson(dt):
    global activePeople, usedPeople
    if len(activePeople) >= config['maximumpeople']:
        return
    
    categoryID = random.randint(1, 6)
    numOptions = len(peopleInfo[categoryID-1])
    personIndex = random.randint(0, numOptions-1)
    personInfo = peopleInfo[categoryID-1][personIndex]

    noInifiteLoop = 0
    while int(personInfo['ID']) in usedPeople and noInifiteLoop < 100:
        personIndex = random.randint(0, numOptions-1)
        personInfo = peopleInfo[categoryID-1][personIndex]
        noInifiteLoop += 1
    
    print(f"New Person ID {personInfo['ID']}")
    
    personURL = peopleImageURLS[int(personInfo['ID']) - 1]
    person = randomizePerson(Person(personURL, personInfo, batch=peopleBatch), config['windowwidth'], config['windowheight'])
    person.setHandler(activePeople)
    

    activePeople.append(person)
    usedPeople.add(int(personInfo['ID']))

def pickActiveCategory():
    global activeCategory
    oldCategory = activeCategory
    while oldCategory == activeCategory:
        activeCategory = random.randint(1, 6)




gameReset(0)
pyglet.app.run(config['framerate'])
