import random

numsBlackJack = [
    "A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "K", "Q", "J"
]*4

def play():
    deck = numsBlackJack.copy()
    random.shuffle(deck)
    
