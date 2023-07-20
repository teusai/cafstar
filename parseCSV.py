import csv

# Note: may be able to decrease process time by using mmap instead

url = 'assets/people-info-id-ordered.csv'

def csvGetRow(n):
    with open(url, newline='') as csvFile:
        reader = csv.DictReader(csvFile, delimiter=',')
        for _ in range(n-1):
            reader.__next__()
        return reader.__next__()


