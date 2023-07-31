def catchPeople(people, catchAreas):
    caughtPeople = filter(lambda p: personInAnyArea(p, catchAreas), people)
    return list(caughtPeople)

def personInArea(person, area):
    position = (person.x, person.y)
    return position in area

def personInAnyArea(person, areas):
    return person.catchable and any([personInArea(person, area) for area in areas])