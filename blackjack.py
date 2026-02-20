import random

numsBlackJack = [
    "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "K", "Q", "J"
]
playerScore = 0
botScore = 0
playerCards = []
botCards = []


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

    return score


def playBlackJack():

    global playerScore, botScore, playerCards, botCards

    playerCards.clear()
    botCards.clear()

    for i in range(2):
        botCards.append(random.choice(numsBlackJack))
        playerCards.append(random.choice(numsBlackJack))

    botScore = calScore(botCards)
    playerScore = calScore(playerCards)


def playerDraw():

    global playerCards, playerScore

    if len(playerCards) < 6 and playerScore < 21:
        playerCards.append(random.choice(numsBlackJack))
        playerScore = calScore(playerCards)
    return playerCards[-1]


def botDraw():

    global botCards, botScore

    if len(botCards) < 6 and botScore < 17:
        botCards.append(random.choice(numsBlackJack))
        botScore = calScore(botCards)
    return botCards[-1]
