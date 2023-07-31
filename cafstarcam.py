"""
Catch A Falling Star            version A.0  7/29/2023

usage:  python cafstarcam.py
Reads cafstar.cfg at the beginning of each game

Tested for Anaconda python 3.11 on Windows 11
Intel RealSense 435 depth camera

To work on camera settings, run:
   python camera.py

Eliot Feibush  call or text:  (609) 462-1609  eliotfeibush@comcast.net
Joseph Symons   jsymons@bgsu.edu
"""


import pyglet
import glob
import random
from Person import Person	# Person.py - handles display of people
import time
import configparser
import readPeople		# readPeople.py
import camera			# camera.py - sets up RealSense camera, acquires images, detects circles
import cv2
import numpy as np


# x,y 0,0 is lower left corner

def readConfigFile(filename):
   global cfg
   cfg = {}		# dictionary of configuration values, available to all functions

   config = configparser.ConfigParser()
   config.sections()
   config.read(filename)

   cfg['highScore'] = int(config['DEFAULT']['highScore'])
   cfg['timeLimit'] = int(config['DEFAULT']['gameTimeLimit'])
   cfg['gameWait'] = int(config['DEFAULT']['gameWaitTime'])
   cfg['backgroundFilename'] = config['DEFAULT']['BackgroundFilename']
   cfg['windowWidth'] = int(config['DEFAULT']['windowWidth'])
   cfg['windowHeight'] = int(config['DEFAULT']['windowHeight'])
   cfg['frameSpeed'] = float(config['DEFAULT']['frameSpeed'])
   cfg['numberCategoryImages'] = int(config['DEFAULT']['numberCategoryImages'])
   cfg['numberNonCategoryImages'] = int(config['DEFAULT']['numberNonCategoryImages'])
   cfg['depthClipMin'] = int(config['DEFAULT']['depthClipMin'])
   cfg['depthClipMax'] = int(config['DEFAULT']['depthClipMax'])
   cfg['detectP1'] = int(config['DEFAULT']['detectP1'])
   cfg['detectP2'] = int(config['DEFAULT']['detectP2'])
   cfg['minRadius'] = int(config['DEFAULT']['minRadius'])
   cfg['maxRadius'] = int(config['DEFAULT']['maxRadius'])
   cfg['minCircleDistance'] = int(config['DEFAULT']['minCircleDistance'])
   cfg['catchDistance'] = int(config['DEFAULT']['catchDistance'])
   cfg['drawDiscs'] = int(config['DEFAULT']['drawDiscs'])
   return cfg

def readCategories(filename):
   global categoryL, categoryColorL
   categoryL = []
   categoryColorL = []

   f = open(filename)
   lines = f.readlines()
   f.close()

   for s in lines:
      #print(s)
      w = s.split(",")
      categoryL.append(w[1])
      colorT = (int(w[2]), int(w[3]), int(w[4]), 255)
      categoryColorL.append(colorT)

def getNextImage(category):
   dd = peopleL[category][nextImg[category]]
   id = dd['ID']
   imgName = people_path + "circle_00" + id + "-transparent.png"
   #print(imgName)

   nextImg[category] += 1
   if nextImg[category] == len(peopleL[category]):
      nextImg[category] = 0		# go back to the first image of the category
      #print("next Image roll over")

   return imgName

def gameInit():
   global timeLimit, startTime, gameTime

   gameScore = 0
   timeLimit = cfg['timeLimit']
   startTime = time.time()
   gameTime = cfg['timeLimit']

def drawScoreboard(dx, dy, gameTime, gameScore):
    font = "Times New Roman"

    colorT = categoryColorL[category]
    borderColorT = (colorT[0], colorT[1], colorT[2])

    batch = pyglet.graphics.Batch()
    arc = pyglet.shapes.Arc(dx+125, dy+125, 125, closed=False, color=borderColorT, batch=batch)
    arc2 = pyglet.shapes.Arc(dx+125, dy+125, 121, closed=False, color=borderColorT, batch=batch)
    circle = pyglet.shapes.Circle(dx+125,dy+125,120,color=(100,100,100), batch=batch)
    circle.opacity = 90
    batch.draw()

    catchT = pyglet.text.Label("Catch", font_name=font, font_size=22, x=dx+90, y=dy+210)
    catchT.draw()

    categoryS = categoryL[category]
    w = categoryS.split("-")
    s1 = w[0].center(21)
    categoryT = pyglet.text.Label(s1, color=colorT, font_name=font, font_size=20, x=dx+30, y=dy+180)
    categoryT.draw()
    s2 = w[1].center(24)
    categoryT = pyglet.text.Label(s2, color=colorT, font_name=font, font_size=20, x=dx+20, y=dy+140)
    categoryT.draw()

    timeT = pyglet.text.Label("Time: " + str(gameTime), color=(255,255,255,255), font_name=font, font_size=20, x=dx+80, y=dy+90)
    timeT.draw()

    scoreT = pyglet.text.Label("Your Score: " + str(gameScore), color=(255,255,255,255), font_name=font, font_size=16, x=dx+60, y=dy+55)
    scoreT.draw()
    highScoreT = pyglet.text.Label("High Score: " + str(highScore), color=(255,255,255,255), font_name=font, font_size=16, x=dx+60, y=dy+28)
    highScoreT.draw()

def load_rand_person():
    index = random.randint(0, num_imgs - 1)
    print(index, people_image_paths[index])
    return Person(people_image_paths[index])

def randomize_person(person):
    person.x = random.randint(person.width//2, cfg['windowWidth']-person.width//2)
    person.y = random.randint(person.height//2, cfg['windowHeight']-person.height//2)
    person.vx = random.randint(50, 200)
    person.vy = random.randint(50, 200)
    return person

def update_person(person, dt):
    person.move(dt)
    person.draw()
    bounding = person.outOfBounds(cfg['windowWidth'], cfg['windowHeight'])
    if bounding:
        if person.vx * bounding[0] < 0 or person.vy * bounding[1] < 0:
            person.bounce(bounding)

def updateScore(gameScore, highScore):
   if gameScore > highScore:
      highScore = gameScore
   
   return gameScore, highScore

def getCatches(people, category, discCenters):
   global gameScore

   # acquire depth image from camera
   # for each pixel:
   #   if depth > maxDepth or depth < minDepth:  pixel = 0
   # find disc centers for pixels >= minDepth

   # for each disc center:
   #   for each person:
   #      if person.caught == False:
   #         if distanceBetween(discCenter, personCenter) < dCatch: # Person.distFromPoint(x,y)
   #            person.caught = True

   #discCenters = [(960,540), (960,1000), (1900,540)]       # for testing without camera
							# Eliot - add blacklist of false positive circles

   for c in discCenters:			# for each disc center:
    for j,p in enumerate(people):		#   for each person:
      if p.caught == False:
       if p.distFromPoint(c[0],c[1]) < catchDistance:		#  check distance
         print(p.x, p.y)
         print("   Caught " + str(j) + " at " + str(c))
         p.caught = True
         if p.category == category:
            gameScore += 1

   return people

def replacePersons(people):
   for j,p in enumerate(people):
      if p.caught == True:		# replace person
         caughtCategory = p.category
         imgName = getNextImage(caughtCategory)
         #print("replace " + str(j) + " category: " + str(caughtCategory))
         currentScale = p.scale
         p = randomize_person(Person(imgName))
         p.setCategory(caughtCategory)
         p.update(scale=currentScale)
         people[j] = p

   return people

def game_loop(dt):
    global gameScore, highScore, people, category
    #print(dt)		# elapsed time since last call to game_loop
    window.clear()

    depthA, rgbA = camera.getFrames(pipeline, depth, color)
    depthA = np.fliplr(depthA)		# flip the depth image from left to right
    depthA = np.flipud(depthA)		# flip the depth image top to bottom
    
    depthA[depthA > depthClipMax] = 0
    depthA[depthA < depthClipMin] = 0	# clear pixels < 2,200 from camera
    depthA = 2 * depthA    # if the environment is clean and there are no false positives then scale up the depth image so the data in range has higher contrast.  This improves circle detection.

    backgroundImg.blit(0,0,0)		# draw the background image      # Eliot - draw depth image for debugging !

    cL, depth_colormap = camera.getCircles(depthA, minCircleDistance, detectP1, detectP2, minRadius, maxRadius)

    discCenterL = []
    for xyr in cL:
        #print(xyr[0], xyr[1], xyr[2])
        center = (int(xyr[0]*1.5), int(xyr[1]*1.5))     # scale 1280x720 depth size to 1920x1080 game coordinates
        discCenterL.append(center)
        radius = int(xyr[2]*1.5)

        if drawDiscs == 1:
           circle = pyglet.shapes.Circle(center[0], center[1], radius, color=(200,200,40))
           circle.draw()

    people = getCatches(people, category, discCenterL)
    people = replacePersons(people)

    currentTime = time.time()
    gameTime = timeLimit - int(currentTime - startTime)
    if gameTime < 0:
       gameTime = 0
    #print(gameTime)

    #if gameTime <= 2:
    label = pyglet.text.Label("Catch A Falling Star", font_name="Times New Roman", font_size=36, x=760, y=850)
    label.draw()

    gameScore, highScore = updateScore(gameScore, highScore)
    drawScoreboard(960-125, 540-125, gameTime, gameScore)

    for person in people:
        update_person(person, dt)

    if currentTime - startTime >= cfg['timeLimit'] + 1:
       print("Game Over")
       print(gameScore)
       time.sleep(cfg['gameWait'])
       pyglet.app.exit()


cfg = readConfigFile("cafstar.cfg")
readCategories("categories.txt")
peopleL = readPeople.readPeople("people.csv")

highScore = cfg['highScore']

backgroundImg = pyglet.image.load(cfg['backgroundFilename'])

people_path = "people_circle_images_RGBA/"

window = pyglet.window.Window(width=cfg['windowWidth'], height=cfg['windowHeight'])
pyglet.gl.glClearColor(0.3, 0.3, 0.3, 1)
pyglet.clock.schedule_interval(game_loop, cfg['frameSpeed'])

people_image_paths = [f for f in glob.glob(people_path + "*.png")]    # 900 image filenames
num_imgs = len(people_image_paths)

nextImg = [0, 0, 0, 0, 0, 0]

depth = True
color = False						# do not need color images from camera, save bandwidth
camCfg, pipeline = camera.setConfig(depth, color)
camera.startStream(camCfg, pipeline)

for j in range(1440):		# run the game repeatedly
   cfg = readConfigFile("cafstar.cfg")
   category = j % 6
   #category = 5				# test next image roll over last image

   nCatImg = cfg['numberCategoryImages']
   nNonCatImg = cfg['numberNonCategoryImages']
   nImg = nCatImg + 5*nNonCatImg

   depthClipMin = cfg['depthClipMin']
   depthClipMax = cfg['depthClipMax']
   detectP1 = cfg['detectP1']
   detectP2 = cfg['detectP2']
   minRadius = cfg['minRadius']
   maxRadius = cfg['maxRadius']
   minCircleDistance = cfg['minCircleDistance']
   catchDistance = cfg['catchDistance']
   drawDiscs = cfg['drawDiscs']

   people = []
   
   for k in range(nCatImg):			# select initial image file names
      imgName = getNextImage(category)
      people.append(randomize_person(Person(imgName)))
      people[-1].setCategory(category)

   for cat in range(6):
      if cat != category:
         #print(cat)
         for n in range(nNonCatImg):
            imgName = getNextImage(cat)
            #print(imgName)
            
            people.append(randomize_person(Person(imgName)))
            people[-1].setCategory(cat)

   imgScale = .1
   for p in people:			# vary the size of the circle images
      p.update(scale=imgScale)
      imgScale += .007

   gameScore = 0
   gameInit()
   pyglet.app.run()


