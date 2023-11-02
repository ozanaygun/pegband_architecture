## Pegband Game Architecture -- Ozan Aygun, Ozlem Yildiz

Required packages:

-- pip install shapely

To run the game: 

python server.py --- Opens the server.

From two different players:

python client.py --- This command needs to be called from two different terminals.


## Board

The game is played on an NxN board where the coordinates are enumerated from 0 to N^2 - 1. Top left coordinate is 0, and the leftmost coordinate on the second row is enumerated as N. 

For N = 5, the board coordinates are as follows:

0  1  2  3  4
5  6  7  8  9
10 11 12 13 14
15 16 17 18 19 
20 21 22 23 24

The first player is chosen as Green (G), and the second player is chosen as Blue (B).

## Game

The game has two phases: peg placement and rubberband placement phases.

Players will play in turns in both rounds.

1- Peg Placement Phase:

Players will choose a location of a peg placement for the current round. The player needs to return an integer between 0 and N^2.

Before the peg placement, the current board state will be sent to the player.

2- Rubberband Placement Phase:

Players will choose edges of rubberbands for the current round. 

The player needs to return a list of integers. Players need to make sure that list of integers are valid coordinates.

IMPORTANT:

- If more than 2 pegs are chosen as edges, the player needs to send pegs in a way that consecutive numbers are neighboring edges. 

For example, if your pegs are placed in this manner:

* * * * * 
* * A * D 
* * * * * 
* B * C * 
* * * * * 

If you want to propose a rubberband placement that encloses 4 pegs with coordinates A,B,C,D; make sure to send one of the lists:

[A, B, C, D],
[B, C, D, A],
[C, B, A, D],
...

Make sure not to send [A, C, D, B], etc.

After two phases, points will be collected and the winner is announced.

## TO DO:

1- For the peg placement phase, fill in the function called "place_pegs()" that returns a single integer.

2- For the rubberband placement phase, fill in the function called "place_rubberbands()" that returns a list of integers.