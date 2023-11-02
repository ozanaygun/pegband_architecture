import socket
import ast
import pegband_player
# Connect to the server
server_ip = '0.0.0.0'
server_port = 4000
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((server_ip, server_port))
client_socket.send("iLan".encode())

# Receive board size and peg placement phase information
board_info = client_socket.recv(8000).decode().strip().split()

#Information for players
# board_length = int(board_info[0])
board_width = int(board_info[1])
num_pegs = int(board_info[2])
num_rubberbands = int(board_info[3])
player_color = int(board_info[4])
player = pegband_player.PegbandPlayer(
  board_width=board_width,
  peg_count=num_pegs,
  band_count=num_rubberbands,
  player_color=player_color
)
# Initialize a list to keep track of peg placements

# Implement the peg placement phase (repeat for num_pegs rounds)
for round in range(num_pegs):
  # Receive the current board with peg positions
  board_str = client_socket.recv(8000).decode()
  board = ast.literal_eval(board_str)
  # Randomly choose a position to place a peg
  position = player.placePegs(round, board)
  # Send the chosen peg position to the server
  client_socket.send(str(position).encode())

for round in range(num_rubberbands):
  # Receive the current board with peg and rubberband positions
  board_str = client_socket.recv(8000).decode()
  board = ast.literal_eval(board_str)
  rubberband_positions = player.placeBands(round, board)
  client_socket.send(str(rubberband_positions).encode())


# Close the client socket
client_socket.close()
