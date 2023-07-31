import csv

def readCategories_old(filename):
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
    
    return categoryL, categoryColorL

def readCategories(filename):
    categories = []

    with open(filename, newline='') as csvFile:
        reader = csv.DictReader(csvFile, delimiter=',')
        for row in reader:
            categories.append(
                {
                    'ID': int(row['ID']),
                    'Name': row['Name'],
                    'Color': (int(row['Red']), int(row['Green']), int(row['Blue']), 255)
                }
            )

    return categories

# print(readCategories('assets/categories.csv'))
