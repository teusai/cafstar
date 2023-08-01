import datetime
import re

def logHighScore(score):
    now = datetime.datetime.now()
    with open("highscores.txt", "a") as file:
        file.write(now.strftime("%Y-%m-%d %H:%M:%S ") + f"{score}\n")

def getHighScores():
    try:
        now = datetime.datetime.now()
        today = now.strftime("%Y-%m-%d")
        with open("highscores.txt", "r") as file:
            dayScore = 0
            conferenceScore = 0
            for line in file:
                score = int(re.search(r'[0-9]{1,3}$', line)[0])
                date = re.search(r'[0-9]{4}-[0-9]{1,2}-[0-9]{1,2}', line)[0]
                conferenceScore = max(conferenceScore, score)
                dayScore = max(dayScore, score) if date == today else dayScore
            return dayScore, conferenceScore
    except OSError as err:
        print("No highscore file yet ->", err)
        return 0, 0


