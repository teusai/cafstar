import csv

# Note: may be able to decrease process time by using mmap instead

url = 'assets/people-info-id-ordered.csv'

def csvGetRow(n):
    with open(url, newline='') as csvFile:
        reader = csv.DictReader(csvFile, delimiter=',')
        for _ in range(n-1):
            reader.__next__()
        return reader.__next__()


def readInfo(filename):
    peopleInfo = ([], [], [], [], [], [])

    with open(filename, newline='') as csvFile:
        reader = csv.DictReader(csvFile, delimiter=',')
        for d in reader:
            peopleInfo[int(d['Category ID'])-1].append(d)

    return peopleInfo

# print(readInfo('assets/people-info-id-ordered.csv'))