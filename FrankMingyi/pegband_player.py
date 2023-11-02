import random

class PegbandPlayer:
    def __init__(self, name, board_length, board_width, board, num_pegs, num_rubberbands, player_color):
        self.name = "Enter your name"
        self.board_length = board_length
        self.board_width = board_width
        self.board = []
        self.num_pegs = num_pegs
        self.num_rubberbands = num_rubberbands
        self.player_color = player_color #1: G, first player -- 2: B, second player.
        self.peg_positions = []

    def place_pegs(self):
        # Fill this function to return your move to place a peg to the board
        position = 0
        return position
    

    def place_rubberbands(self):
        # Fill this function to return your move to place your rubberbands to the pegs
        temp = []
        return temp