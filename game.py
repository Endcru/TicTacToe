import pygame
import sys
from flask import Flask
import json
import time
import requests
import threading

DOMAIN = "127.0.0.1:5000"

player = 0
curTurn = 0

pygame.init()
response = requests.get("http://"+DOMAIN+"/connect")
jwks = response.json()
print(response)
if response.status_code == 200:
    connection = True
    player = jwks['player']
    if player == 0:
        pygame.display.set_caption("Крестики-нолики X")
    else:
        pygame.display.set_caption("Крестики-нолики O")
else:
    pygame.quit()
    sys.exit(0)
print(jwks)

size_block = 100
margin = 15
width = heigth = size_block * 3 + margin * 4

size_window = (width, heigth)
screen = pygame.display.set_mode(size_window)
black = (0, 0, 0)
white = (255, 255, 255)
mas = [[0] * 3 for i in range (3)]
gameActive = True

def drawGame():
    for row in range(3):
        for col in range(3):
            x = col * size_block + (col + 1) * margin
            y = row * size_block + (row + 1) * margin
            if mas[row][col] == 'x':
                pygame.draw.line(screen, black, (x+5,y+5), (x + size_block - 5, y + size_block - 5), 3)
                pygame.draw.line(screen, black, (x + size_block - 5,y+5), (x + 5, y + size_block - 5), 3)
            elif mas[row][col] == 'o':
                pygame.draw.circle(screen, black, (x+size_block//2, y+size_block//2), size_block//2-3,3)
            else:
                pygame.draw.rect(screen, white, (x, y, size_block, size_block))
    pygame.display.update()

def victory(type):
    global gameActive
    gameActive = False
    screen.fill(black)
    font = pygame.font.SysFont('stxingkai', 80)
    textl = font.render(type, True, white)
    text_rext = textl.get_rect()
    text_x = screen.get_width() / 2 - text_rext.width / 2
    text_y = screen.get_height() / 2 - text_rext.height / 2
    screen.blit(textl, [text_x, text_y])
    pygame.display.update()
    time.sleep(2)
    currentScore()

def gameEndLeave():
    global gameActive
    gameActive = False
    screen.fill(black)
    font = pygame.font.SysFont('stxingkai', 55)
    textl = font.render('Противник вышел', True, white)
    text_rext = textl.get_rect()
    text_x = screen.get_width() / 2 - text_rext.width / 2
    text_y = screen.get_height() / 2 - text_rext.height / 2
    screen.blit(textl, [text_x, text_y])
    pygame.display.update()
    time.sleep(2)
    currentScore()

def gameDraw():
    global gameActive
    gameActive = False
    screen.fill(black)
    font = pygame.font.SysFont('stxingkai', 80)
    textl = font.render('Ничья', True, white)
    text_rext = textl.get_rect()
    text_x = screen.get_width() / 2 - text_rext.width / 2
    text_y = screen.get_height() / 2 - text_rext.height / 2
    screen.blit(textl, [text_x, text_y])
    pygame.display.update()
    time.sleep(2)
    currentScore()

def currentScore():
    global mas, curTurn, gameActive
    response = requests.get("http://"+DOMAIN+"/current_score")
    x = response.json()['xwins']
    y = response.json()['owins']
    screen.fill(black)
    font = pygame.font.SysFont('stxingkai', 80)
    textl = font.render('Счёт', True, white)
    textl1 = font.render('Победы X - ' + str(x), True, white)
    textl2 = font.render('Победы O - ' + str(y), True, white)
    text_rext = textl.get_rect()
    text_rext1 = textl1.get_rect()
    text_rext2 = textl2.get_rect()
    text_x = screen.get_width() / 2 - text_rext.width / 2
    text_y = screen.get_height() / 2 - text_rext.height / 2
    text_x1 = screen.get_width() / 2 - text_rext1.width / 2
    text_x2 = screen.get_width() / 2 - text_rext2.width / 2
    screen.blit(textl, [text_x, text_y - 80])
    screen.blit(textl1, [text_x1, text_y])
    screen.blit(textl2, [text_x2, text_y + 80])
    pygame.display.update()
    time.sleep(2)
    screen.fill(black)
    mas = [[0] * 3 for i in range (3)]
    curTurn = 0
    gameActive = True
    drawGame()

def connection():
    while connection:
        response = requests.post("http://"+DOMAIN+"/connection", json={'player': player})
        time.sleep(5)

drawGame()
    
thread = threading.Thread(target=connection, daemon=True)
thread.start()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            response = requests.delete("http://"+DOMAIN+"/exit", json={'player': player})
            pygame.quit()
            sys.exit(0)
        elif event.type == pygame.MOUSEBUTTONDOWN and curTurn % 2 == player and gameActive:
            x_mouse, y_mouse = pygame.mouse.get_pos()
            col = x_mouse // (size_block + margin)
            row = y_mouse // (size_block + margin)
            if col >= 2:
                col = 2
            if col < 0:
                col = 0
            if row >= 2:
                row = 2
            if row < 0:
                row = 0
            if mas[row][col] == 0:
                curTurn += 1
                if player == 0:
                    mas[row][col] = 'x'
                    response = requests.post("http://"+DOMAIN+"/xturn", json={'row': row, 'col': col})
                    drawGame()
                    if (response.json()['victory']):
                        victory('x')
                    if (response.json()['gameDraw']):
                        gameDraw()
                else:
                    mas[row][col] = 'o'
                    response = requests.post("http://"+DOMAIN+"/oturn", json={'row': row, 'col': col})
                    drawGame()
                    if (response.json()['victory']):
                        victory('o')
                    if (response.json()['gameDraw']):
                        gameDraw()
        if curTurn % 2 != player:
            response = requests.get("http://"+DOMAIN+"/curturn")
            if response.status_code == 200:
                if (response.json()['gameEnd']):
                    gameEndLeave()
                    response = requests.delete("http://"+DOMAIN+"/exit", json={'player': player})
                    connection = False
                    pygame.quit()
                    sys.exit(0)
                servTurn = response.json()['curTurn']
                if servTurn != curTurn:
                    time.sleep(0.5)
                    continue
                curTurn += 1 
                row = response.json()['row']
                col = response.json()['col']
                if player == 0:
                    mas[row][col] = 'o'
                else:
                    mas[row][col] = 'x'
                drawGame()
                if (response.json()['victory']):
                    if player == 0:
                        victory('o')
                    else:
                        victory('x')
                if (response.json()['gameDraw']):
                        gameDraw()
                 