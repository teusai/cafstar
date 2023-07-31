import pyglet

def drawScoreboard(width, height, ratio, gameScore, gameTime, category):
    center_x = width // 2
    center_y = height // 2
    diameter = width * ratio
    radius = diameter / 2

    font = "Open Sans"

    colorT = category['Color']
    borderColorT = (colorT[0], colorT[1], colorT[2])

    batch = pyglet.graphics.Batch()
    arc = pyglet.shapes.Arc(center_x, center_y, radius=radius, closed=False, color=borderColorT, batch=batch)
    arc2 = pyglet.shapes.Arc(center_x, center_y, radius=radius+3, closed=False, color=borderColorT, batch=batch)
    circle = pyglet.shapes.Circle(center_x, center_y, radius=radius, color=(0, 0, 0), batch=batch)
    circle.opacity = 255
    batch.draw()

    catchT = pyglet.text.Label("Catch", font_name=font, font_size=26, x=center_x, y=center_y+(radius/1.25), anchor_x='center', anchor_y='center')
    catchT.draw()

    categoryS = category['Name']
    name = " ".join(categoryS.split("-"))
    categoryT = pyglet.text.Label(name, color=colorT, font_name=font, font_size=14, x=center_x, y=center_y+(radius/2), anchor_x='center', anchor_y='center')
    categoryT.draw()
    # w = categoryS.split("-")
    # s1 = w[0].center(21)
    # categoryT = pyglet.text.Label(s1, color=colorT, font_name=font, font_size=20, x=dx+30, y=dy+180)
    # categoryT.draw()
    # s2 = w[1].center(24)
    # categoryT = pyglet.text.Label(s2, color=colorT, font_name=font, font_size=20, x=dx+20, y=dy+140)
    # categoryT.draw()

    timeT = pyglet.text.Label("Time: " + f"{gameTime:.0f}", color=(255,255,255,255), font_name=font, font_size=20, x=center_x, y=center_y, anchor_x='center', anchor_y='center')
    timeT.draw()

    scoreT = pyglet.text.Label("Your Score: " + str(gameScore), color=(255,255,255,255), font_name=font, font_size=16, x=center_x, y=center_y-(radius/2), anchor_x='center', anchor_y='center')
    scoreT.draw()
    # highScoreT = pyglet.text.Label("High Score: " + str(highScore), color=(255,255,255,255), font_name=font, font_size=16, x=dx+60, y=dy+28)
    # highScoreT.draw()

    # Delete everything from memory
    arc.delete()
    arc2.delete()
    circle.delete()
    catchT.delete()
    categoryT.delete()
    timeT.delete()
    scoreT.delete()
    # highScoreT.delete()