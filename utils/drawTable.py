import pyglet
import math

def drawScoreboard(width, height, ratio, scores, gameTime, category, image=None):
    center_x, center_y, radius = getMeasurements(width, height, ratio)

    gameScore = scores[0]
    dayScore = scores[1]
    conferenceScore = scores[2]

    font = "Open Sans"
    fontColor = (254, 246, 232, 255)
    borderColor = (255, 230, 155, 255)
    mainFontSize = radius / 15
    numberFontSize = mainFontSize + 8


    batch = pyglet.graphics.Batch()

    table = pyglet.shapes.Circle(center_x, center_y, radius=radius, color=(0, 0, 0, 255))

    time = pyglet.text.Label("Time", color=fontColor, font_name=font, font_size=mainFontSize, x=center_x, y=center_y+(radius*0.85), anchor_x='center', anchor_y='center', batch=batch)
    remaining = pyglet.text.Label("Remaining:", color=fontColor, font_name=font, font_size=mainFontSize, x=center_x, y=center_y+(radius*0.75), anchor_x='center', anchor_y='center', batch=batch)
    timeLabel = pyglet.text.Label(f"{int(gameTime)}", color=fontColor, font_name=font, font_size=numberFontSize, x=center_x, y=center_y+(radius*0.45), anchor_x='center', anchor_y='center', batch=batch)
    boxWidth = numberFontSize * 3
    boxHeight = numberFontSize * 3
    timeBorder = pyglet.shapes.BorderedRectangle(x=center_x-(boxWidth//2), y=center_y+(radius*0.45)-(boxHeight//2), width=boxWidth, height=boxHeight, border=6, color=(0,0,0), border_color=borderColor, batch=batch)


    catch = pyglet.text.Label("Catch:", font_name=font, font_size=mainFontSize, color=fontColor, x=center_x, y=center_y+(radius*0.18), anchor_x='center', anchor_y='center', batch=batch)
    boxWidth = radius * 1.8
    boxHeight = radius * 0.2
    catchBorder = pyglet.shapes.BorderedRectangle(x=center_x-(boxWidth//2), y=center_y-(boxHeight//2), width=boxWidth, height=boxHeight, border=6, color=category["Color"], border_color=borderColor, batch=batch)
    catchLabel = pyglet.text.Label(category["Name"], color=(255,255,255,255), font_name=font, font_size=mainFontSize, x=center_x, y=center_y, anchor_x='center', anchor_y="center", batch=batch)

    
    yourScore = pyglet.text.Label("Your Score: ", color=fontColor, font_name=font, font_size=mainFontSize, x=center_x, y=center_y-(radius*0.18), anchor_x='center', anchor_y='center', batch=batch)
    scoreLabel = pyglet.text.Label(f"{gameScore}", color=fontColor, font_name=font, font_size=numberFontSize, x=center_x+(radius*0.4), y=center_y-(radius*0.18), anchor_x='center', anchor_y='center', batch=batch)

    highScore = pyglet.text.Label("High Scores", color=fontColor, font_name=font, font_size=mainFontSize, x=center_x, y=center_y-(radius*0.4), anchor_x='center', anchor_y='center', batch=batch)
    highScoreLabel = pyglet.text.Label(f"Day: {dayScore} Conference: {conferenceScore}", color=fontColor, font_name=font, font_size=mainFontSize, x=center_x, y=center_y-(radius*0.55), anchor_x='center', anchor_y='center', batch=batch)

    draw(table, batch, image)

def drawGameOver(width, height, ratio, scores, image=None):
    center_x, center_y, radius = getMeasurements(width, height, ratio)

    gameScore = scores[0]
    dayScore = scores[1]
    conferenceScore = scores[2]

    font = "Open Sans"
    fontColor = (254, 246, 232, 255)
    borderColor = (255, 230, 155, 255)
    mainFontSize = radius / 15
    numberFontSize = mainFontSize + 4


    batch = pyglet.graphics.Batch()

    table = pyglet.shapes.Circle(center_x, center_y, radius=radius, color=(0, 0, 0, 255))

    gameOver = pyglet.text.Label("Game Over", color=borderColor, font_name=font, font_size=mainFontSize*2, x=center_x, y=center_y+(radius*0.2), anchor_x='center', anchor_y='center', batch=batch)

    
    yourScore = pyglet.text.Label("Your Score: ", color=fontColor, font_name=font, font_size=mainFontSize, x=center_x, y=center_y-(radius*0.18), anchor_x='center', anchor_y='center', batch=batch)
    scoreLabel = pyglet.text.Label(f"{gameScore}", color=fontColor, font_name=font, font_size=numberFontSize, x=center_x+(radius*0.4), y=center_y-(radius*0.18), anchor_x='center', anchor_y='center', batch=batch)

    highScore = pyglet.text.Label("High Scores", color=fontColor, font_name=font, font_size=mainFontSize, x=center_x, y=center_y-(radius*0.4), anchor_x='center', anchor_y='center', batch=batch)
    highScoreLabel = pyglet.text.Label(f"Day: {dayScore} Conference: {conferenceScore}", color=fontColor, font_name=font, font_size=mainFontSize, x=center_x, y=center_y-(radius*0.55), anchor_x='center', anchor_y='center', batch=batch)

    draw(table, batch, image)


def drawStartScreen(width, height, ratio, image=None):
    center_x, center_y, radius = getMeasurements(width, height, ratio)

    font = 'Open Sans'
    fontColor = (254, 246, 232, 255)
    borderColor = (255, 230, 155, 255)
    titleFontSize = radius / 10
    mainFontSize = radius / 15

    batch = pyglet.graphics.Batch()

    table = pyglet.shapes.Circle(center_x, center_y, radius=radius, color=(0, 0, 0, 255))

    line1 = pyglet.text.Label("Catch a Falling Star:", x=center_x, y=center_y+(radius*0.6), font_name=font, color=borderColor, font_size=titleFontSize, anchor_x='center', anchor_y='center', batch=batch)
    line2 = pyglet.text.Label("The People of", x=center_x, y=center_y+(radius*0.45), font_name=font, color=borderColor, font_size=titleFontSize, anchor_x='center', anchor_y='center', batch=batch)
    line3 = pyglet.text.Label("SIGGRAPH Game", x=center_x, y=center_y+(radius*0.3), font_name=font, color=borderColor, font_size=titleFontSize, anchor_x='center', anchor_y='center', batch=batch)

    line4 = pyglet.text.Label("You have", x=center_x, y=center_y-(radius*0.3), font_name=font, color=fontColor, font_size=mainFontSize, anchor_x='center', anchor_y='center', batch=batch)
    line5 = pyglet.text.Label("20 seconds", x=center_x, y=center_y-(radius*0.4), font_name=font, color=fontColor, font_size=mainFontSize, anchor_x='center', anchor_y='center', batch=batch)
    line6 = pyglet.text.Label("to catch as many SIGGRAPH", x=center_x, y=center_y-(radius*0.5), font_name=font, color=fontColor, font_size=mainFontSize, anchor_x='center', anchor_y='center', batch=batch)
    line7 = pyglet.text.Label("community members", x=center_x, y=center_y-(radius*0.6), font_name=font, color=fontColor, font_size=mainFontSize, anchor_x='center', anchor_y='center', batch=batch)
    line8 = pyglet.text.Label("as you can.", x=center_x, y=center_y-(radius*0.7), font_name=font, color=fontColor, font_size=mainFontSize, anchor_x='center', anchor_y='center', batch=batch)

    draw(table, batch, image)

def getMeasurements(width, height, ratio):
    center_x = width // 2
    center_y = height // 2
    radius = width * ratio * 0.5
    return center_x, center_y, radius

def draw(table, batch, image):
    table.draw()
    if image:
        # image.scale = (table.radius / image.width)
        image.draw()
    batch.draw()