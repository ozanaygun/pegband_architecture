import socket
import random
import ast
import time
import pegband_player1
import pegband_player2
import pegband_player
import threading
import multiprocessing

# Connect to the server
server_ip = '0.0.0.0'
server_port = 4000
player = pegband_player1.PegbandPlayer1(0, 0, [], 0, 0, 0, 0)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((server_ip, server_port))
client_socket.send(str(player.name).encode())
global remaining_time
remaining_time = 120

# Receive board size and peg placement phase information
board_info = client_socket.recv(2048).decode().strip().split()

#Information for client
board_length = int(board_info[0])
board_width = int(board_info[1])
num_pegs = int(board_info[2])
num_rubberbands = int(board_info[3])
board = []

def run_with_timeout(func, player):

    def wrapper():
        #nonlocal remaining_time
        start_time = time.time()
        func()
        end_time = time.time()
        elapsed_time = end_time - start_time
        remaining_time -= elapsed_time

    p = multiprocessing.Process(target=wrapper)
    p.start()
    p.join(remaining_time)
    if p.is_alive():
        p.terminate()
        print(f"Time limit has been exceeded by {player.name}!")
        # Close the client socket
        client_socket.close()
    else:
        print(f"{player.name}, Remaining time: {remaining_time} seconds.")

#pegs = [9, 25, 31, 6]

#Information for players
player.board_length = int(board_info[0])
player.board_width = int(board_info[1])
player.num_pegs = int(board_info[2])
player.num_rubberbands = int(board_info[3])
player.player_color = int(board_info[4])
# Initialize a list to keep track of peg placements

# Implement the peg placement phase (repeat for num_pegs rounds)
for round in range(num_pegs):
    # Receive the current board with peg positions
    board_str = client_socket.recv(2048).decode()
    board = ast.literal_eval(board_str)
    player.board = board
    # Randomly choose a position to place a peg
    position = player.place_pegs()
    #position = pegs[round]
    # Send the chosen peg position to the server
    client_socket.send(str(position).encode())

#player.peg_positions = pegs

for round in range(num_rubberbands):
    # Receive the current board with peg and rubberband positions
    board_str = client_socket.recv(2048).decode()
    player.board = ast.literal_eval(board_str)
    start_time = time.time()
    rubberband_positions = player.place_rubberbands()
    end_time = time.time()
    client_socket.send(str(rubberband_positions).encode())


# Close the client socket
client_socket.close()
