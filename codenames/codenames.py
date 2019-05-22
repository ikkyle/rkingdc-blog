import random

with open('data/wordlist.txt', 'r') as wf:
    codewords = wf.read().splitlines()
    
codewords = [w for w in codewords if w != '']

def create_game(codewords):
    board = random.sample(codewords, k=25)
    red = random.sample(board, k=8)
    blue = random.sample(list(set(board) - set(red)), k=7)
    black = random.sample(
        list(set(board) - set(blue) - set(red)),
        k=1
    )
    return board, red, blue, black
