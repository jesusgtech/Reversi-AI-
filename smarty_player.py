#Zijie Zhang, Sep.24/2023


import numpy as np
import socket, pickle
from reversi import reversi


# POSITIONAL WEIGHT TABLE (added)
# Assigns a strategic value to each cell on the board.
#   Corners (100)   -> Best cells, can never be flipped once taken
#   X-squares (-40) -> Diagonal to corners, dangerous (gives opponent corner)
#   C-squares (-20) -> Edge cells next to corners, also risky
#   Edges (10)      -> Stable once claimed, good to take
#   Center (1-5)    -> Neutral, minor value

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


# HELPER: get all valid moves for a player on a given board (added)
# Returns a list of (row, col, flips_count)

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

# HELPER: apply a move and return the resulting new board (added)

def apply_move(board, x, y, turn):
    game = reversi()
    game.board = board.copy()
    game.step(x, y, turn, True)  # commit=True to update game.board
    return game.board.copy()


# 1-STEP LOOKAHEAD SCORING (added)
#
# How it works:
#   1. Score MY move:  positional weight of where I land + pieces I flip
#   2. Simulate board after my move
#   3. Find OPPONENT's best response on that new board (same scoring)
#   4. Final score = my_score - opponent's_best_score

def score_move(i, j, my_flips, board_after_my_move, my_turn):
    opponent = -my_turn

    # My move score: positional value of the cell + bonus for each piece flipped
    my_score = WEIGHT_TABLE[i][j] + my_flips * 2

    # Simulate what the opponent would do on the new board
    opp_moves = get_valid_moves(board_after_my_move, opponent)

    if not opp_moves:
        # Opponent has no moves at all — great outcome for us! Big bonus.
        best_opp_score = -50
    else:
        # Find opponent's best possible score (greedy + positional weight)
        best_opp_score = max(
            WEIGHT_TABLE[oi][oj] + opp_flips * 2
            for (oi, oj, opp_flips) in opp_moves
        )

    # Our final score = what we gain minus what we let the opponent gain
    return my_score - best_opp_score

def main():
    game_socket = socket.socket()
    game_socket.connect(('127.0.0.1', 33333))
    game = reversi()

    while True:

        #Receive play request from the server
        #turn : 1 --> you are playing as white | -1 --> you are playing as black
        #board : 8*8 numpy array
        data = game_socket.recv(4096)
        turn, board = pickle.loads(data)

        #Turn = 0 indicates game ended
        if turn == 0:
            game_socket.close()
            return
        
        #Debug info
        print(turn)
        print(board)


        # ORIGINAL SMARTY LOGIC (unchanged) - greedy + edge preference
        # This runs first and picks the fallback move in case the
        # lookahead below finds nothing better.

        x = -1
        y = -1
        ex = -1 #look for best edge play
        ey = -1
        max = 0
        maxEdge = 0
        game.board = board
        for i in range(8):
            for j in range(8):
                cur = game.step(i, j, turn, False)
                if i == 0 or i == 7:    #look for best edge play
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

        # Original smarty edge-preference decision
        if maxEdge > max-1 and ex != -1:
            fallback_x, fallback_y = ex, ey
        else:
            fallback_x, fallback_y = x, y

        # 1-STEP LOOKAHEAD (added on top)
        # Scores each valid move by also simulating the opponent's best
        # response. Falls back to the original smarty result above if
        # no moves are found (shouldn't happen, just a safety net).

        best_score = float('-inf')
        best_x, best_y = fallback_x, fallback_y  # start with smarty fallback

        moves = get_valid_moves(board, turn)
        for (i, j, flips) in moves:
            new_board = apply_move(board, i, j, turn)
            score = score_move(i, j, flips, new_board, turn)
            if score > best_score:
                best_score = score
                best_x, best_y = i, j

        #Send your move to the server. Send (x,y) = (-1,-1) to tell the server you have no hand to play
        game_socket.send(pickle.dumps([best_x, best_y]))
        

if __name__ == '__main__':
    main()
