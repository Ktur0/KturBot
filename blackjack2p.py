import random

numsBlackJack = [
    "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "K", "Q", "J"
]

def calScore(player):

    score = 0

    if player[0] == "1" and player[1] == "1":
        return "AA"

    for i in range(len(player)):
        if i == 2 and score < 21 and "1" in player[:2]:
            score -= 10

        if i < 2:
            if player[i] == "1":
                score += 11
            elif player[i] in ["K", "Q", "J"]:
                score += 10
            else:
                score += int(player[i])
        else:
            if player[i] in ["K", "Q", "J"]:
                score += 10
            else:
                score += int(player[i])
    
    if len(player) == 5 and score <= 21:
        return "5 perfect cards"

    return score

def draw():
    return random.choice(numsBlackJack)