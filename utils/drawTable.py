import pyglet

def drawScoreboard(width, height, ratio, scores, gameTime, category, image=None):
    center_x = width // 2
    center_y = height // 2
    diameter = width * ratio
    radius = diameter / 2

    gameScore = scores[0]
    dayScore = scores[1]
    conferenceScore = scores[2]

    font = "Open Sans"
    fontColor = (254, 246, 232, 255)
    borderColor = (255, 230, 155, 255)
    mainFontSize = radius / 15
    numberFontSize = mainFontSize + 8


    batch = pyglet.graphics.Batch()

    table = pyglet.shapes.Circle(center_x, center_y, radius=radius, color=(0, 0, 0, 255), batch=batch)

    time = pyglet.text.Label("Time", color=fontColor, font_name=font, font_size=mainFontSize, x=center_x, y=center_y+(radius*0.8), anchor_x='center', anchor_y='center', batch=batch)
    remaining = pyglet.text.Label("Remaining:", color=fontColor, font_name=font, font_size=mainFontSize, x=center_x, y=center_y+(radius*0.7), anchor_x='center', anchor_y='center', batch=batch)
    timeLabel = pyglet.text.Label(f"{int(gameTime)}", color=fontColor, font_name=font, font_size=numberFontSize, x=center_x, y=center_y+(radius*0.45), anchor_x='center', anchor_y='center', batch=batch)
    timeLabel.bold = True
    circle = pyglet.shapes.Arc(x=center_x, y=center_y+(radius*0.45), radius=numberFontSize*1.5, color=borderColor, batch=batch)


    catch = pyglet.text.Label("Catch:", font_name=font, font_size=mainFontSize, color=fontColor, x=center_x, y=center_y+(radius*0.18), anchor_x='center', anchor_y='center', batch=batch)
    boxWidth = radius * 1.8
    boxHeight = radius * 0.2
    catchBorder = pyglet.shapes.BorderedRectangle(x=center_x-(boxWidth//2), y=center_y-(boxHeight//2), width=boxWidth, height=boxHeight, border=6, color=(0,0,0), border_color=borderColor, batch=batch)
    catchLabel = pyglet.text.Label(category["Name"], color=category["Color"], font_name=font, font_size=mainFontSize, x=center_x, y=center_y, anchor_x='center', anchor_y="center", batch=batch)
    catchLabel.bold = True

    
    yourScore = pyglet.text.Label("Your Score: ", color=fontColor, font_name=font, font_size=mainFontSize, x=center_x, y=center_y-(radius*0.18), anchor_x='center', anchor_y='center', batch=batch)
    scoreLabel = pyglet.text.Label(f"{gameScore}", color=fontColor, font_name=font, font_size=numberFontSize, x=center_x+(radius*0.4), y=center_y-(radius*0.18), anchor_x='center', anchor_y='center', batch=batch)

    highScore = pyglet.text.Label("High Scores", color=fontColor, font_name=font, font_size=mainFontSize, x=center_x, y=center_y-(radius*0.4), anchor_x='center', anchor_y='center', batch=batch)
    highScoreLabel = pyglet.text.Label(f"Day: {dayScore} Conference: {conferenceScore}", color=fontColor, font_name=font, font_size=mainFontSize, x=center_x, y=center_y-(radius*0.55), anchor_x='center', anchor_y='center', batch=batch)

    if image:
        image.draw()
    batch.draw()

def drawGameOver(width, height, ratio, scores, image=None):
    center_x = width // 2
    center_y = height // 2
    diameter = width * ratio
    radius = diameter / 2

    gameScore = scores[0]
    dayScore = scores[1]
    conferenceScore = scores[2]

    font = "Open Sans"
    fontColor = (254, 246, 232, 255)
    borderColor = (255, 230, 155, 255)
    mainFontSize = radius / 15
    numberFontSize = mainFontSize + 4


    batch = pyglet.graphics.Batch()

    table = pyglet.shapes.Circle(center_x, center_y, radius=radius, color=(0, 0, 0, 255), batch=batch)

    gameOver = pyglet.text.Label("Game Over", color=borderColor, font_name=font, font_size=mainFontSize*2, x=center_x, y=center_y+(radius*0.2), anchor_x='center', anchor_y='center', batch=batch)

    
    yourScore = pyglet.text.Label("Your Score: ", color=fontColor, font_name=font, font_size=mainFontSize, x=center_x, y=center_y-(radius*0.18), anchor_x='center', anchor_y='center', batch=batch)
    scoreLabel = pyglet.text.Label(f"{gameScore}", color=fontColor, font_name=font, font_size=numberFontSize, x=center_x+(radius*0.4), y=center_y-(radius*0.18), anchor_x='center', anchor_y='center', batch=batch)

    highScore = pyglet.text.Label("High Scores", color=fontColor, font_name=font, font_size=mainFontSize, x=center_x, y=center_y-(radius*0.4), anchor_x='center', anchor_y='center', batch=batch)
    highScoreLabel = pyglet.text.Label(f"Day: {dayScore} Conference: {conferenceScore}", color=fontColor, font_name=font, font_size=mainFontSize, x=center_x, y=center_y-(radius*0.55), anchor_x='center', anchor_y='center', batch=batch)

    if image:
        image.draw()
    batch.draw()
