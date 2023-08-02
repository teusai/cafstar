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
import camera
import numpy as np
import gc

config = readConfig('cafstar.cfg')
peopleInfo = readInfo('assets/people-info-id-ordered.csv')
categories = readCategories('assets/categories.csv')

print('Loading assets')

# people images
peopleImageURLS = sorted(glob.glob('assets/people_new/*.png'))
for i, url in enumerate(peopleImageURLS):
    peopleImageURLS[i] = url.replace('\\', '/')

peopleImages = [pyglet.resource.image(url) for url in peopleImageURLS]
numTotalPeople = len(peopleImageURLS)
for i, p in enumerate(peopleImages):
    p.width = 1200
    p.height = 1200
    p.anchor_x = p.width // 2
    p.anchor_y = p.height // 2
    
print('Loaded people images')


# catch animation
catchAnimSourceURLS = sorted(glob.glob('assets/Caught-it_circle_anim/*.png'))
for i, url in enumerate(catchAnimSourceURLS):
    catchAnimSourceURLS[i] = url.replace('\\', '/') 

catchAnimSourceFrames = [pyglet.resource.image(url) for url in catchAnimSourceURLS]

for f in catchAnimSourceFrames:
    f.anchor_x = f.width // 2
    f.anchor_y = f.height // 2
catchAnimSource = pyglet.image.Animation.from_image_sequence(catchAnimSourceFrames, duration=0.01, loop=False)
print('Loaded catch animations')

# background animation
backgroundURLS = sorted(glob.glob('assets/Background animation/*.jpg'))
for i, url in enumerate(backgroundURLS):
    backgroundURLS[i] = url.replace('\\', '/')

frames = [pyglet.resource.image(f) for f in backgroundURLS]
backgroundSource = pyglet.image.Animation.from_image_sequence(frames, duration=0.1)
backgroundAnim = pyglet.sprite.Sprite(img=backgroundSource)
backgroundAnim.scale = config['backgroundscale']
print('Loaded background animations')

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
print('Loaded table stars')

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
    
    depth_image = 0
    color_image = 0
    catchAreas = [catcher]
    
    got_frame, depth_image, color_image = camera.getFrames(pipeline, depth, color)

    if got_frame == True:
        depth_image[depth_image > config['depthclipmax']] = 0
        depth_image[depth_image < config['depthclipmin']] = 0
        depth_image[depth_image > 0] = 65535

        circleList, depth_colormap = camera.getCircles(depth_image, config['mincircledistance'], config['detectp1'], config['detectp2'], int(config['minradius']), int(config['maxradius']))

        # camera.cv2.imshow('RealSense', depth_colormap)
        
        for xyr in circleList:
            center = (int(xyr[0]) * 1.5, int(xyr[1] * 1.5))
            radius = int(xyr[2] * 1.5)
            catchAreas.append(pyglet.shapes.Circle(center[0], center[1], radius, color=(200, 200, 40)))

    backgroundAnim.draw()
    for area in catchAreas:
        area.draw()
    
    peopleBatch.draw()
    scores = (currentScore, dayHighScore, conferenceHighScore)
    drawTable.drawScoreboard(config['windowwidth'], config['windowheight'], config['tabletowindowratio'], scores, remainingTime, categories[activeCategory-1], tableStarSprite)

    caughtPeople = catchPeople(activePeople, catchAreas, activeCategory)
    if caughtPeople:
        # print(caughtPeople)
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
    categoryID = activeCategory if random.randint(1,3) == 1 else categoryID
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
    # print(color)
    sprite.color = (color[0], color[1], color[2])

depth = True
color = False
camera_config, pipeline = camera.setConfig(depth, color)
camera.startStream(camera_config, pipeline)

testest = 123451

gameReset(0)
pyglet.app.run(config['framerate'])

camera.stopStreaming(pipeline)