#Zijie Zhang, Sep.24/2023

import numpy as np
import socket, pickle
from reversi import reversi

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

        #Local Greedy - Replace with your algorithm
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
        #Send your move to the server. Send (x,y) = (-1,-1) to tell the server you have no hand to play
        if maxEdge > max-1:
            game_socket.send(pickle.dumps([ex,ey]))
        else:
            game_socket.send(pickle.dumps([x,y]))
        
        
if __name__ == '__main__':
    main()