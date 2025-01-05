from flask import Flask, jsonify, make_response, request, abort
import time

DOMAIN = "127.0.0.1:5000"

app = Flask(__name__)

player0 = False
player1 = False
player0timer = True
player1timer = True
mas = [[0] * 3 for i in range (3)]
curTurn = -1
row = 0
col = 0
victory = False
gameEnd = False
xwins = 0
owins = 0
gameDraw = False
EndRequest = 0
timeDiscinnection = 30

def checkVictory():
    for i in range(3):
        if mas[i][0] != 0 and mas[i][0] == mas[i][1] and mas[i][0] == mas[i][2]:
            return True
        if mas[0][i] != 0 and mas[0][i] == mas[1][i] and mas[0][i] == mas[2][i]:
            return True
    if mas[0][0] != 0 and mas[0][0] == mas[1][1] and mas[0][0] == mas[2][2]:
        return True
    if mas[0][2] != 0 and mas[0][2] == mas[1][1] and mas[0][2] == mas[2][0]:
        return True
    return False

def reGame():
    global mas, curTurn, victory, gameEnd, gameDraw, EndRequest
    mas = [[0] * 3 for i in range (3)]
    curTurn = -1
    victory = False
    gameEnd = False
    gameDraw = False
    EndRequest = 0
    
    
@app.route('/connect', methods=['GET'])
def connect():
    global player0, player1, player0timer, player1timer
    if not player0:
        player0 = True
        player0timer = time.time()
        return make_response(jsonify({'player': 0}), 200)
    if not player1:
        player1 = True
        player1timer = time.time()
        return make_response(jsonify({'player': 1}), 200)
    return make_response(jsonify({'player': -1}), 503)

@app.route('/connection', methods=['POST'])
def connection():
    global player0timer, player1timer, gameEnd, EndRequest, player0, player1
    if not request.json or not 'player' in request.json:
        abort(400)
    if request.json['player'] == 0:
        player0timer = time.time()
        if abs(time.time() - player1timer) >= timeDiscinnection and player1:
            gameEnd = True
            player1 = False
            EndRequest = 1
    elif request.json['player'] == 1:
        player1timer = time.time()
        if abs(time.time() - player0timer) >= timeDiscinnection and player0:
            gameEnd = True
            player0 = False
            EndRequest = 1
    return make_response(jsonify(), 200)

@app.route('/xturn', methods=['POST'])
def xturn():
    global row, col, curTurn, victory, xwins, gameDraw
    if not request.json or not 'col' in request.json or not 'row' in request.json:
        abort(400)
    row = request.json['row']
    col = request.json['col']
    curTurn += 1
    mas[row][col] = 'x'
    if checkVictory():
        victory = True
        xwins += 1
        return make_response(jsonify({'victory': True, 'gameDraw': False}), 200)
    if curTurn == 8:
        gameDraw = True
        return make_response(jsonify({'victory': False, 'gameDraw': True}), 200)
    return make_response(jsonify({'victory': False, 'gameDraw': False}), 200)

@app.route('/oturn', methods=['POST'])
def yturn():
    global row, col, curTurn, victory, owins, gameDraw
    if not request.json or not 'col' in request.json or not 'row' in request.json:
        abort(400)
    row = request.json['row']
    col = request.json['col']
    curTurn += 1
    mas[row][col] = 'o'
    if checkVictory():
        victory = True
        owins += 1
        return make_response(jsonify({'victory': True, 'gameDraw': False}), 200)
    if curTurn == 8:
        gameDraw = True
        return make_response(jsonify({'victory': False, 'gameDraw': True}), 200)
    return make_response(jsonify({'victory': False, 'gameDraw': False}), 200)

@app.route('/curturn', methods=['GET'])
def curturn():
    global EndRequest
    return make_response(jsonify({'curTurn': curTurn, 'row': row, 'col': col, 'victory': victory, 'gameEnd': gameEnd, 'gameDraw': gameDraw}), 200)

@app.route('/current_score', methods=['GET'])
def currentScore():
    global EndRequest
    x = xwins
    y = owins
    EndRequest += 1
    if (EndRequest >= 2):
        reGame()
    return make_response(jsonify({'xwins': x, 'owins': y}), 200)

@app.route('/exit', methods=['DELETE'])
def exit():
    global player0, player1, gameEnd, EndRequest, xwins, owins
    if not request.json or not 'player' in request.json:
        abort(400)
    if request.json['player'] == 0:
        player0 = False
        gameEnd = True
    elif request.json['player'] == 1:
        player1 = False
        gameEnd= True
    else:
        abort(400)
    if (not player0 and not player1):
        xwins = 0
        owins = 0
        reGame()
    return make_response(jsonify(), 200)
        
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == '__main__':
    app.run()

