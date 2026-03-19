#Zijie Zhang, Sep.24/2023


import numpy as np
import socket, pickle
from reversi import reversi

WEIGHT_TABLE = np.array([
    [100, -20, 10,  5,  5, 10, -20, 100],
    [-20, -40, -5, -5, -5, -5, -40, -20],
    [ 10,  -5,  1,  1,  1,  1,  -5,  10],
    [  5,  -5,  1,  1,  1,  1,  -5,   5],
    [  5,  -5,  1,  1,  1,  1,  -5,   5],
    [ 10,  -5,  1,  1,  1,  1,  -5,  10],
    [-20, -40, -5, -5, -5, -5, -40, -20],
    [100, -20, 10,  5,  5, 10, -20, 100],
], dtype=float)

def get_dynamic_weights(board, turn):
    weights = WEIGHT_TABLE.copy()

    # Top-left corner
    if board[0][0] == turn:
        weights[0][1] = 5
        weights[1][0] = 5
        weights[1][1] = 5
    elif board[0][0] == -turn:
        weights[0][1] = -50
        weights[1][0] = -50
        weights[1][1] = -50

    # Top-right corner
    if board[0][7] == turn:
        weights[0][6] = 5
        weights[1][7] = 5
        weights[1][6] = 5
    elif board[0][7] == -turn:
        weights[0][6] = -50
        weights[1][7] = -50
        weights[1][6] = -50

    # Bottom-left corner
    if board[7][0] == turn:
        weights[7][1] = 5
        weights[6][0] = 5
        weights[6][1] = 5
    elif board[7][0] == -turn:
        weights[7][1] = -50
        weights[6][0] = -50
        weights[6][1] = -50

    # Bottom-right corner
    if board[7][7] == turn:
        weights[7][6] = 5
        weights[6][7] = 5
        weights[6][6] = 5
    elif board[7][7] == -turn:
        weights[7][6] = -50
        weights[6][7] = -50
        weights[6][6] = -50

    return weights

def get_valid_moves(board, turn):
    game = reversi()
    game.board = board.copy()
    moves = []
    for i in range(8):
        for j in range(8):
            flips = game.step(i, j, turn, False)  
            if flips > 0:
                moves.append((i, j, flips))
    return moves


def apply_move(board, x, y, turn):
    game = reversi()
    game.board = board.copy()
    game.step(x, y, turn, True)  
    return game.board.copy()


def score_move(i, j, my_flips, board_after_my_move, my_turn, weights):
    opponent = -my_turn
    my_score = weights[i][j] + my_flips * 2
    opp_moves = get_valid_moves(board_after_my_move, opponent)
    mobility_penalty = len(opp_moves) * 3

    if not opp_moves:
        best_opp_score = -100
    else:
        opp_weights = get_dynamic_weights(board_after_my_move, opponent)
        best_opp_score = max(
            opp_weights[oi][oj] + opp_flips * 0.5
            for (oi, oj, opp_flips) in opp_moves
        )

    return my_score - best_opp_score - mobility_penalty

def main():
    game_socket = socket.socket()
    game_socket.connect(('127.0.0.1', 33333))
    game = reversi()

    while True:
        data = game_socket.recv(4096)
        turn, board = pickle.loads(data)

        if turn == 0:
            game_socket.close()
            return

        print(turn)
        print(board)

        x = -1
        y = -1
        ex = -1 
        ey = -1
        max = 0
        maxEdge = 0
        game.board = board
        for i in range(8):
            for j in range(8):
                cur = game.step(i, j, turn, False)
                if i == 0 or i == 7:   
                    if cur > maxEdge:
                        maxEdge = cur
                        ex, ey = i, j
                elif j == 0 or j == 7:
                    if cur > maxEdge:
                        maxEdge = cur
                        ex, ey = i, j

                if cur > max:
                    max = cur
                    x, y = i, j

        if maxEdge > max-1 and ex != -1:
            fallback_x, fallback_y = ex, ey
        else:
            fallback_x, fallback_y = x, y

        best_score = float('-inf')
        best_x, best_y = fallback_x, fallback_y  

        weights = get_dynamic_weights(board, turn)
        moves = get_valid_moves(board, turn)
        for (i, j, flips) in moves:
            new_board = apply_move(board, i, j, turn)
            score = score_move(i, j, flips, new_board, turn, weights)
            if score > best_score:
                best_score = score
                best_x, best_y = i, j

        game_socket.send(pickle.dumps([best_x, best_y]))
        

if __name__ == '__main__':
    main()
