def catchPeople(people, catcherList, activeCategory, catchDistance):
    caughtPeople = []
    for person in people:
        for catcher in catcherList:
            if person.caught == False:
                if person.category == activeCategory:
                    if person.distFromPoint(catcher[0], catcher[1]) < catchDistance:
                        caughtPeople.append(person)
    return caughtPeople