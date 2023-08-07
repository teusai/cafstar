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

peopleImageSize = 800

# people images
peopleImageURLS = sorted(glob.glob('assets/people/*.png'))
for i, url in enumerate(peopleImageURLS):
    peopleImageURLS[i] = url.replace('\\', '/')

peopleImages = [pyglet.resource.image(url) for url in peopleImageURLS]
numTotalPeople = len(peopleImageURLS)
for i, p in enumerate(peopleImages):
    p.width = peopleImageSize
    p.height = peopleImageSize
    p.anchor_x = p.width // 2
    p.anchor_y = p.height // 2
    
print('Loaded people images: ' + str(len(peopleImages)))

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
backgroundSource = pyglet.image.Animation.from_image_sequence(frames, duration=0.04)
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


window = pyglet.window.Window(width=int(config['windowwidth']), height=int(config['windowheight']), style='borderless')
# window = pyglet.window.Window(width=800, height=600)

gameState = 0

activePeople = []
usedPeople = set()

currentScore = 0
dayHighScore, conferenceHighScore = highscores.getHighScores()
scores = (currentScore, dayHighScore, conferenceHighScore)

remainingTime = config['gametimelimit']
activeCategory = 1

DrawTable = drawTable.DrawTable(config['windowwidth'], config['windowheight'], config['tabletowindowratio'], scores, remainingTime, categories[activeCategory-1], tableStarSprite)
catcherMouse = [0, 0, discRadius]
# catcherList = [catcherMouse]
catcherList = []
catchAnimBatch = pyglet.graphics.Batch()

depth = True
color = False
camera_config, pipeline = camera.setConfig(depth, color)

# @window.event
# def on_mouse_motion(x, y, dx, dy):
#     global catcherMouse
#     catcherMouse[0] = x
#     catcherMouse[1] = y

@window.event
def on_refresh(dt):
    global remainingTime, currentScore, dayHighScore, conferenceHighScore, catcherList, catcherMouse, depth, color
    window.clear()
    backgroundAnim.draw()
    if gameState == 0:
        scores = (currentScore, dayHighScore, conferenceHighScore)
        if remainingTime > config['gamewaittime'] / 2:
            DrawTable.drawGameOver(config['windowwidth'], config['windowheight'], config['tabletowindowratio'], scores, tableStarSprite)
        else:
            DrawTable.drawStartScreen(config['windowwidth'], config['windowheight'], config['tabletowindowratio'], tableStarSprite)
    elif gameState == 1:
        loopBatch = pyglet.graphics.Batch()
        
        depth_image = 0
        color_image = 0
        # catcherList = [catcherMouse]
        catcherList = []
        
        got_frame, depth_image, color_image = camera.getFrames(pipeline, depth, color)

        if got_frame == True:
            depth_image[depth_image > config['depthclipmax']] = 0
            depth_image[depth_image < config['depthclipmin']] = 0
            depth_image[depth_image > 0] = 65535

            circleList, depth_colormap = camera.getCircles(depth_image, config['mincircledistance'], config['detectp1'], config['detectp2'], int(config['minradius']), int(config['maxradius']))

            # camera.cv2.imshow('RealSense', depth_colormap)
            
            for xyr in circleList:
                center = (int(xyr[0]) * 1.5, int(xyr[1] * 1.5))
                radius = xyr[2] * 1.5
                newCatcher = [center[0], center[1], radius]
                catcherList.append(newCatcher)

        # catcherCircles = []
        # for catcher in catcherList:
        #     catcherCircles.append(pyglet.shapes.Circle(catcher[0], catcher[1], catcher[2], color=(200, 200, 40), batch=loopBatch))

        activeSprites = []
        for activePerson in activePeople:
            activeSprites.append(pyglet.sprite.Sprite(peopleImages[int(activePerson.info['ID'])-1], x=activePerson.x, y=activePerson.y, batch=loopBatch))
            activeSprites[-1].rotation = activePerson.rotation
            activeSprites[-1].opacity = activePerson.opacity
            activeSprites[-1].scale = activePerson.scale
            # bounding = activePerson.outOfBounds(config['windowwidth'], config['windowheight'])
            # if bounding:
            #     if activePerson.vx * bounding[0] < 0 or activePerson.vy * bounding[1] < 0:
            #         activePerson.bounce(bounding)
            activePerson.step(dt)
        
        caughtPeople = catchPeople(activePeople, catcherList, config['catchdistance'], config['windowwidth'], config['windowheight'])
        if caughtPeople:
            # print(caughtPeople)
            caughtSprites = []
            for caughtPerson in caughtPeople:
                caughtPerson.timeLimit = 0
                caughtPerson.caught = True
                currentScore += 1
                if caughtPerson.category == activeCategory:
                    caughtSprites.append(pyglet.sprite.Sprite(catchAnimSource, x=caughtPerson.x, y=caughtPerson.y, batch=catchAnimBatch))
                    color = categories[caughtPerson.category-1]['Color']
                    caughtSprites[-1].color = (color[0], color[1], color[2])
                    currentScore += 1
                pickActiveCategory()

        loopBatch.draw()
        catchAnimBatch.draw()

        scores = (currentScore, dayHighScore, conferenceHighScore)
        DrawTable.drawScoreboard(config['windowwidth'], config['windowheight'], config['tabletowindowratio'], scores, remainingTime, categories[activeCategory-1], tableStarSprite)

    remainingTime -= dt


def gameReset(dt):
    global gameState, DrawTable, activePeople, usedPeople, currentScore, dayHighScore, conferenceHighScore, remainingTime, catchAnimBatch
    
    gameState = 1

    for p in activePeople:
        p.despawn()
    del activePeople
    del usedPeople
    del catchAnimBatch
    catchAnimBatch = pyglet.graphics.Batch()
    
    activePeople = []
    usedPeople = set()
    
    currentScore = 0
    dayHighScore, conferenceHighScore = highscores.getHighScores()
    remainingTime = config['gametimelimit']

    print(gc.get_count())
    gc.collect()
    print(gc.get_count())

    pickActiveCategory()

    pyglet.clock.schedule_interval(spawnPerson, config['personspawnrate'])
    pyglet.clock.schedule_once(gameEnd, config['gametimelimit'])

def gameEnd(dt):
    print("game ended")
    global gameState, remainingTime
    gameState = 0
    remainingTime = config['gamewaittime']
    highscores.logHighScore(currentScore)
    pyglet.clock.unschedule(spawnPerson)
    pyglet.clock.schedule_once(gameReset, config['gamewaittime'])

def spawnPerson(dt):
    global activePeople, usedPeople, peopleImageSize
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
    
    person = randomizePerson(Person(personIndex, personInfo), config['windowwidth'], config['windowheight'])
    person.setHandler(activePeople)
    activePeople.append(person)
    usedPeople.add(int(personInfo['ID']))
    # print(len(activePeople))

def pickActiveCategory():
    global activeCategory
    oldCategory = activeCategory
    while oldCategory == activeCategory:
        activeCategory = random.randint(1, 6)


camera.startStream(camera_config, pipeline)

gameReset(0)
pyglet.app.run(config['framerate'])

camera.stopStreaming(pipeline)