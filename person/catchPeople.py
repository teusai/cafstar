import math

def catchPeople(people, catcherList, activeCategory, catchDistance, width, height):
    caughtPeople = []
    for person in people:
        for catcher in catcherList:
            if person.caught == False:
                if person.category == activeCategory:
                    if person.distFromPoint(catcher[0], catcher[1]) < catchDistance:
                        if math.sqrt((catcher[0]-width/2)*(catcher[0]-width/2) + (catcher[1]-height/2)*(catcher[1]-height/2)) > 320:
                            caughtPeople.append(person)
    return caughtPeople