def catchPeople(people, catchAreas, activeCategory):
    caughtPeople = filter(lambda p: personInAnyArea(p, catchAreas, activeCategory), people)
    return list(caughtPeople)

def personInArea(person, area):
    position = (person.x, person.y)
    return position in area

def personInAnyArea(person, areas, activeCategory):
    return (person.category == activeCategory) and (not person.caught) and any([personInArea(person, area) for area in areas])