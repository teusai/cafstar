import pyglet
import random
import glob
from person.person import Person
from person.catchPeople import catchPeople
from person.personUtils import randomizePerson
from utils.readConfig import readConfig
from utils.readInfo import readInfo
from utils.readCategories import readCategories
import utils.drawTable as drawTable
import highscores

import gc
import os


config = readConfig('cafstar.cfg')
peopleInfo = readInfo('assets/people-info-id-ordered.csv')
categories = readCategories('assets/categories.csv')
peopleImageURLS = sorted(glob.glob('assets/people/*.png'))
numTotalPeople = len(peopleImageURLS)
catchAnim = pyglet.image.Animation.from_image_sequence(
    pyglet.image.ImageGrid(
        pyglet.resource.image("resources/anim_star1_6x6_255sq_00000.png"),
        rows=6, columns=6
    ),
    duration=0.1
)

backgroundPlayer = pyglet.media.Player()
backgroundPlayer.loop = True
background = pyglet.media.load('assets/' + config['backgroundfilename'])
backgroundPlayer.queue(background)
print(backgroundPlayer.source)
print(f'FFMPEG? {pyglet.media.have_ffmpeg()}')

discRadius = config['disctowindowratio'] * config['windowwidth'] * 0.5


window = pyglet.window.Window(width=config['windowwidth'], height=config['windowheight'])
pyglet.gl.glClearColor(0.3, 0.3, 0.3, 1)

catcher = pyglet.shapes.Circle(0, 0, radius=discRadius)

@window.event
def on_mouse_motion(x, y, dx, dy):
    global catcher
    catcher.x = x
    catcher.y = y


activePeople = []
usedPeople = set()
peopleBatch = pyglet.graphics.Batch()
dayHighScore = 0
conferenceHighScore = 0
currentScore = 0
activeCategory = 1
catchAreas = [pyglet.shapes.Circle(x=400, y=300, radius=discRadius), catcher]
remainingTime = config['gametimelimit']


def gameReset(dt):
    pyglet.clock.unschedule(gameWait)
    # backgroundPlayer.play()
    global activePeople, usedPeople, currentScore, dayHighScore, conferenceHighScore, remainingTime, peopleBatch
    for p in activePeople:
        p.despawn()
    del activePeople
    del usedPeople
    del peopleBatch
    activePeople = []
    usedPeople = set()
    peopleBatch = pyglet.graphics.Batch()
    currentScore = 0
    dayHighScore, conferenceHighScore = highscores.getHighScores()
    remainingTime = config['gametimelimit']

    print(gc.get_count())
    gc.collect()
    print(gc.get_count())

    pickActiveCategory()

    pyglet.clock.schedule_interval(gameLoop, config['framerate'])
    pyglet.clock.schedule_interval(spawnPerson, config['personspawnrate'])
    pyglet.clock.schedule_once(gameEnd, config['gametimelimit'])


def gameLoop(dt):
    window.clear()
    global remainingTime, currentScore

    if remainingTime < 0:
        print("game ended")
        return

    # print("game looping")
    # backgroundImage.blit(0, 0)
    if backgroundPlayer.source and backgroundPlayer.source.video_format:
        print('video exists and stuff')
        backgroundPlayer.texture.blit(0,0)
    for area in catchAreas:
        area.draw()
    
    peopleBatch.draw()
    scores = (currentScore, dayHighScore, conferenceHighScore)
    drawTable.drawScoreboard(config['windowwidth'], config['windowheight'], config['tabletowindowratio'], scores, remainingTime, categories[activeCategory-1])

    caughtPeople = catchPeople(activePeople, catchAreas)
    if caughtPeople:
        print(caughtPeople)
        for p in caughtPeople:
            p.timeLimit = 0
            p.caught = True
            if p.category == activeCategory:
                startCatchAnim(p)
                currentScore += 1
                pickActiveCategory()


    for person in activePeople:
        # bounding = person.outOfBounds(config['windowwidth'], config['windowheight'])
        # if bounding:
        #     if person.vx * bounding[0] < 0 or person.vy * bounding[1] < 0:
        #         person.bounce(bounding)
        person.step(dt)
    
    
    remainingTime -= dt


def gameEnd(dt):
    pyglet.clock.unschedule(gameLoop)
    pyglet.clock.unschedule(spawnPerson)
    highscores.logHighScore(currentScore)
    global remainingTime
    remainingTime = config['gamewaittime']
    pyglet.clock.schedule_interval(gameWait, config['framerate'])
    pyglet.clock.schedule_once(gameReset, config['gamewaittime'])

def gameWait(dt):
    global remainingTime
    # backgroundImage.blit(0,0)
    window.clear()
    scores = (currentScore, dayHighScore, conferenceHighScore)
    drawTable.drawGameOver(config['windowwidth'], config['windowheight'], config['tabletowindowratio'], scores)
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
    
    # print(f"New Person ID {personInfo['ID']}")
    
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

def startCatchAnim(person):
    return
    sprite = pyglet.sprite.Sprite(catchAnim, x=person.x, y=person.y, anchor_x='center', anchor_y='center', batch=peopleBatch)
    color = categories[person.category-1]['Color']
    print(color)
    sprite.color = (color[0], color[1], color[2])






gameReset(0)
pyglet.app.run(config['framerate'])
