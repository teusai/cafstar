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



config = readConfig('cafstar.cfg')
peopleInfo = readInfo('assets/people-info-id-ordered.csv')
categories = readCategories('assets/categories.csv')

# people images
peopleImageURLS = sorted(glob.glob('assets/people/*.png'))
for i, url in enumerate(peopleImageURLS):
    peopleImageURLS[i] = url.replace('\\', '/')

peopleImages = [pyglet.resource.image(url) for url in peopleImageURLS]
numTotalPeople = len(peopleImageURLS)
for p in peopleImages:
    p.anchor_x = p.width // 2
    p.anchor_y = p.height // 2


# catch animation
catchAnimSourceURLS = sorted(glob.glob('assets/Caught-it_circle_anim/*.png'))
for i, url in enumerate(catchAnimSourceURLS):
    catchAnimSourceURLS[i] = url.replace('\\', '/') 

catchAnimSourceFrames = [pyglet.resource.image(url) for url in catchAnimSourceURLS]

for f in catchAnimSourceFrames:
    f.anchor_x = f.width // 2
    f.anchor_y = f.height // 2
catchAnimSource = pyglet.image.Animation.from_image_sequence(catchAnimSourceFrames, duration=0.01, loop=False)

# background animation
backgroundURLS = sorted(glob.glob('assets/Background animation/*.png'))
for i, url in enumerate(backgroundURLS):
    backgroundURLS[i] = url.replace('\\', '/')

frames = [pyglet.resource.image(f) for f in backgroundURLS]
backgroundSource = pyglet.image.Animation.from_image_sequence(frames, duration=0.1)
backgroundAnim = pyglet.sprite.Sprite(img=backgroundSource)
backgroundAnim.scale = config['backgroundscale']

# table stars animation
tableStarURLS = sorted(glob.glob('assets/Star_animation/*-transparent.png'))
for i, url in enumerate(tableStarURLS):
    tableStarURLS[i] = url.replace('\\', '/')

tableStarFrames = [pyglet.resource.image(f) for f in tableStarURLS]
for f in tableStarFrames:
    f.anchor_x = f.width // 2
    f.anchor_y = f.height // 2
tableStarAnim = pyglet.image.Animation.from_image_sequence(tableStarFrames, duration=0.3)
tableStarSprite = pyglet.sprite.Sprite(tableStarAnim, x=config['windowwidth']//2, y=config['windowheight']//2)
tableStarSprite.scale = (config['windowwidth'] * config['tabletowindowratio']) / tableStarSprite.width

discRadius = config['disctowindowratio'] * config['windowwidth'] * 0.5


window = pyglet.window.Window(width=int(config['windowwidth']), height=int(config['windowheight']))
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
catchAreas = [catcher]
remainingTime = config['gametimelimit']


def gameReset(dt):
    pyglet.clock.unschedule(gameWait)
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
    # if backgroundPlayer.source and backgroundPlayer.source.video_format:
    #     print('video exists and stuff')
    #     backgroundPlayer.texture.blit(0,0)
    backgroundAnim.draw()
    for area in catchAreas:
        area.draw()
    
    peopleBatch.draw()
    scores = (currentScore, dayHighScore, conferenceHighScore)
    drawTable.drawScoreboard(config['windowwidth'], config['windowheight'], config['tabletowindowratio'], scores, remainingTime, categories[activeCategory-1], tableStarSprite)

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
    window.clear()
    backgroundAnim.draw()
    scores = (currentScore, dayHighScore, conferenceHighScore)
    if remainingTime > config['gamewaittime'] / 2:
        drawTable.drawGameOver(config['windowwidth'], config['windowheight'], config['tabletowindowratio'], scores, tableStarSprite)
    else:
        drawTable.drawStartScreen(config['windowwidth'], config['windowheight'], config['tabletowindowratio'], tableStarSprite)
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
    
    personImage = peopleImages[int(personInfo['ID']) - 1]
    person = randomizePerson(Person(personImage, personInfo, batch=peopleBatch), config['windowwidth'], config['windowheight'])
    person.setHandler(activePeople)
    

    activePeople.append(person)
    usedPeople.add(int(personInfo['ID']))

def pickActiveCategory():
    global activeCategory
    oldCategory = activeCategory
    while oldCategory == activeCategory:
        activeCategory = random.randint(1, 6)

def startCatchAnim(person):
    sprite = pyglet.sprite.Sprite(catchAnimSource, x=person.x, y=person.y, batch=peopleBatch)
    sprite.anchor_x = 'center'
    sprite.anchor_y = 'center'
    color = categories[person.category-1]['Color']
    print(color)
    sprite.color = (color[0], color[1], color[2])






gameReset(0)
pyglet.app.run(config['framerate'])
