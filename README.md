Reversi-AI-

Smarty_player is an enchanted version of greedy_player that thinks beyond and predicts the opponent's best response to its move. It reads the board and evaluates the best move for the current player based on the positional weight table and the number of pieces flipped. It also considers the opponent's best response to its move and chooses the move that maximizes its score.

How it works

It uses a positional weight table to evaluate the value of each cell on the board.

Corners (100) -> Best cells, can never be flipped once taken
X-squares (-40) -> Diagonal to corners, dangerous (gives opponent corner)
C-squares (-20) -> Edge cells next to corners, also risky
Edges (10) -> Stable once claimed, good to take
Center (1-5) -> Neutral, minor value
It considers the opponent's best response to its move and chooses the move that maximizes its score.

Score MY move: positional weight of where I land + pieces I flip
Simulate board after my move
Find OPPONENT's best response on that new board (same scoring)
Final score = my_score - opponent's_best_score
It uses a greedy approach to find the best move for the current player.

It uses a greedy approach to find the best move for the opponent.

It chooses the move that maximizes its score.

How to run

Start the server (Terminal 1)
python reversi_server.py