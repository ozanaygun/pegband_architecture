import socket
import ast
import time
import math
import matplotlib.path as mpath
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
from shapely.ops import cascaded_union
import multiprocessing

# Define the game board size and initial state
board_size = (20, 20)
num_pegs = 6
num_rubberbands = 4
#### Remaining times
remaining_time = [120, 120]
board = [0] * (board_size[0] * board_size[1])
# Initialize the server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', 4000))
server.listen(2)

class Player:
    def __init__(self, name, socket, color):
        self.name = name
        self.socket = socket
        self.color = color
        self.point = 0
        self.board = []
        self.peg_board = []
        self.peg_coordinates = []
        self.rubberband_coordinates = []

def display_board(board, board_length, board_width):

    mapping = {
        0: '*',
        1: 'G',
        2: 'B',
        3: 'g',
        4: 'b'
    }

    for i in range(board_length):
        for j in range(board_width):
            index = i * board_length + j
            print(mapping.get(board[index], '?'), end=' ')
        print()

def rubberband_validity(peg1, peg2, board_size, enemy_pegs):
    check_cross_move = False
    illegal_cross_move = False
    start_peg = min(peg1, peg2)
    end_peg = max(peg1, peg2)

    x1 = int(start_peg%board_size[1])
    y1 = int(start_peg/board_size[0])+1
    x2 = int(end_peg%board_size[1])
    y2 = int(end_peg/board_size[0])+1

    positions = []  # List to store the positions the rubberband passes through

    vertical_diff = y1-y2
    horizontal_diff = x1-x2
    left_or_right = -1
    if(horizontal_diff >= 0):
        left_or_right *= 1
    else:
        left_or_right *= -1
    up_or_down = -1
    if(vertical_diff >= 0):
        up_or_down *= 1
    else:
        up_or_down *= -1

    if(horizontal_diff == 0):
        for i in range(abs(vertical_diff) + 1):
            positions.append(start_peg + up_or_down * board_size[0]*i)
    elif(vertical_diff == 0):
        for i in range(abs(horizontal_diff) + 1):
            positions.append(start_peg + left_or_right * i)
    # Diagonal move
    elif(abs(vertical_diff) == abs(horizontal_diff)):
        for i in range(abs(vertical_diff)+1):
            positions.append(start_peg + (up_or_down*i*board_size[0] + (left_or_right*(i))))
    #Cross move
    else:
        check_cross_move = True
        current_row = y1

        x1 += 0.5
        x2 += 0.5
        y1 -= 0.5
        y2 -= 0.5

        temp_x = x1
        temp_y = y1

        multiplier = 1
        if(vertical_diff * horizontal_diff < 0):
            multiplier = -1

        for i in range(abs(vertical_diff)):
            temp_increase = 0.5 + 1*i
            temp_y = y1 + temp_increase
            shift = multiplier * abs(horizontal_diff)*temp_increase/abs(vertical_diff)

            if(multiplier == 1):
                start = math.floor(temp_x)
                end = math.ceil(x1 + shift)
            else:
                end = math.ceil(temp_x)
                start = math.floor(x1 + shift)
            
            for j in range(end - start):
                candidate_x = (start + 0.5) + j
                candidate_y = current_row - 0.5
                
                positions.append(int((candidate_y-0.5)*board_size[0] + (candidate_x-0.5)))

            temp_x = x1 + shift
            current_row += 1

        temp_increase += 0.5
        temp_y = y2
        shift = multiplier * abs(horizontal_diff)*temp_increase/abs(vertical_diff)

        if(multiplier == 1):
            start = math.floor(temp_x)
            end = math.ceil(x1 + shift)
        else:
            end = math.ceil(temp_x)
            start = math.floor(x1 + shift)

        for j in range(end - start):
            candidate_x = (start + 0.5) + j
            candidate_y = current_row - 0.5
            
            positions.append(int((candidate_y-0.5)*board_size[0] + (candidate_x-0.5)))

        # Check if there is any enemy pegs in between for cross move
        for i in range(len(enemy_pegs)):
            cur_x = int(enemy_pegs[i]%board_size[1])
            cur_y = int(enemy_pegs[i]/board_size[0])+1
            # Line equation between pegs, check if it goes from any of the enemy pegs, illegal move.
            slope = vertical_diff/horizontal_diff
            if((cur_x - x1)*slope == (cur_y - y1)):
                illegal_move = True

    return positions, check_cross_move, illegal_cross_move


# Expand the polygon slightly to account for grid center intersections
def expand_polygon(polygon_points, expansion_factor=0.001):
    if len(polygon_points) < 3:
        return polygon_points
    polygon = Polygon(polygon_points)
    expanded_polygon = polygon.buffer(expansion_factor)
    return list(expanded_polygon.exterior.coords)

# Check if the polygon is convex
def is_convex(polygon_points):
    if len(polygon_points) < 3:
        return True
    polygon = Polygon(polygon_points)
    convex_hull = polygon.convex_hull
    return polygon.equals(convex_hull)


def check_inside_rubberband(player_peg_coordinates, enemy_peg_coordinates, proposed_rubberband, board_size):
    points = []
    for i in range(len(proposed_rubberband)):
        x1 = (int(proposed_rubberband[i]%board_size) + 0.5) 
        y1 = -1*(int(proposed_rubberband[i]/board_size)+1 - 0.5 - board_size)
        points.append([x1, y1])
    x1 = int(proposed_rubberband[0]%board_size) + 0.5 
    y1 = -1*(int(proposed_rubberband[0]/board_size)+1 - 0.5 - board_size)
    points.append([x1, y1])

    # Expand the polygon
    expanded_points = expand_polygon(points)

    # Check convexity
    if is_convex(expanded_points):
        convex_check = True
    else:
        convex_check = False

    grid_centers = [[0.5 + x, 0.5 + y] for y in range(board_size) for x in range(board_size)]
    # Create a Path object from the expanded polygon points
    path = mpath.Path(expanded_points)

    # Initialize a list to store the grid centers inside the polygon
    grid_centers_inside_polygon = []
    center_locations_inside_polygon = []

    # Check each grid center if it's inside the polygon
    for center in grid_centers:
        if path.contains_point(center):
            #if center not in points:
            grid_centers_inside_polygon.append(center)  
            center_locations_inside_polygon.append(int((center[1]*(-1) + board_size + 0.5 - 1)*(board_size) + (center[0] - 0.5))) 
    
    return convex_check, center_locations_inside_polygon

# Create player objects and store them in a list
players = []
for i in range(2):
    print(f"Waiting for Player {i + 1} to connect...")
    player_socket, player_address = server.accept()
    player_name = player_socket.recv(2048).decode()
    print(player_name)
    print(f"Player {i + 1}: {player_name} is connected.")
    players.append(Player(player_name, player_socket, i))

# Send board size and peg placement phase information to both players
board_info_1 = f"{board_size[0]} {board_size[1]} {num_pegs} {num_rubberbands} {1}\n".encode()
players[0].socket.send(board_info_1)
board_info_2 = f"{board_size[0]} {board_size[1]} {num_pegs} {num_rubberbands} {2}\n".encode()
players[1].socket.send(board_info_2)

time.sleep(0.3)

######
# Peg placement phase 
for round in range(num_pegs):
    player_index = 1
    other_player_index = 2
    for player in players:
        try:
            # Send the current board with peg positions
            player.socket.send(str(board).encode())
            start_time = time.time()
            position = int(player.socket.recv(2048).decode())
            end_time = time.time()
            remaining_time[player_index-1] -= end_time - start_time
            print(f"Remaining time for {player.name}: {remaining_time[player_index-1]}")
            # Update the board with the player's peg
            if(position >= 0 and position < board_size[0] * board_size[1]):
                if(board[position] == player_index):
                    print(f"{player.name}, you have already placed a peg in this position!")
                elif(board[position] == other_player_index):
                    print(f"{players[other_player_index-1].name} has a peg in this position! No peg is placed by {player.name}!")
                else:
                    board[position] = player_index  # Alternates between Player 1 and Player 2
                    player.peg_coordinates.append(position)
                    print(f"{player.name} placed a peg at location {position}.")
            else:
                print(f"Coordinate out of range! No peg is placed by {player.name}!")
            player_index = 2
            other_player_index = 1
        except Exception as e:
            print(f"Invalid coordinate! No peg is placed by {player.name}!")


player.socket.send(str(board).encode())
players[0].board = board.copy()
players[0].peg_board = board.copy()
players[1].board = board.copy()
players[1].peg_board = board.copy()

# Display the board
print("Initial board")
display_board(board, board_size[0], board_size[1])
print("-----")
print("Rubberband placement phase")
print("-----")
time.sleep(0.3)
#########
# Rubberband placement phase 
for round in range(num_rubberbands):
    player_index = 1
    other_player = 2
    for player in players:
        cross_move = False
        illegal_cross_move = False
        illegal_move = False
        temp_points = 0
        temp_rubberband = []
        player.socket.send(str(player.board).encode())
        start_time = time.time()
        rubberband_edges_str = player.socket.recv(2048).decode()
        end_time = time.time()
        remaining_time[player_index-1] -= end_time - start_time
        print(f"Rubberband has been placed. Remaining time for {player.name}: {remaining_time[player_index-1]}")
        rubberband_edges = ast.literal_eval(rubberband_edges_str)
        ## Rubberband validity conditions
        proposed_rubberband = []
        if(len(rubberband_edges) == 1):
            proposed_rubberband = rubberband_edges
        #If there is only a line of connection
        elif(len(rubberband_edges) == 2):
            proposed_rubberband, check_cross_move, bad_cross_move = rubberband_validity(rubberband_edges[0], rubberband_edges[1], board_size, players[other_player-1].peg_coordinates)
            if(check_cross_move):
                cross_move = True
            if(bad_cross_move):
                illegal_cross_move = True          
            temp_points = len(proposed_rubberband)
        elif(len(rubberband_edges) > 2):
            for i in range(len(rubberband_edges) - 1):
                temp_rubberband, check_cross_move, bad_cross_move = rubberband_validity(rubberband_edges[i], rubberband_edges[i+1], board_size, players[other_player-1].peg_coordinates)
                if(check_cross_move):
                    cross_move = True
                if(bad_cross_move):
                    illegal_cross_move = True
                for j in range(len(temp_rubberband)):
                    proposed_rubberband.append(temp_rubberband[j])
            temp_rubberband, check_cross_move, bad_cross_move = rubberband_validity(rubberband_edges[len(rubberband_edges)-1], rubberband_edges[0], board_size, players[other_player-1].peg_coordinates)
            if(check_cross_move):
                cross_move = True
            if(bad_cross_move):
                illegal_cross_move = True
            for j in range(len(temp_rubberband)):
                proposed_rubberband.append(temp_rubberband[j])

            proposed_rubberband = list(set(proposed_rubberband))

            convexity_check, pegs_inside = check_inside_rubberband(player.peg_coordinates, players[other_player-1].peg_coordinates, rubberband_edges, board_size[0])

            #print(f"Centers inside the polygon: {pegs_inside}")
            #print(f"Enemy peg coordinates: {players[other_player-1].peg_coordinates}")

            if(not convexity_check):
                illegal_move = True
                print(f"The polygon is not convex! No rubberband placed by {player.name}")
            for i in range(len(pegs_inside)):
                if(pegs_inside[i] in players[other_player-1].peg_coordinates):
                    print("There is an enemy peg inside the polygon!")
                    illegal_move = True
                else:
                    if(pegs_inside[i] not in proposed_rubberband):
                        proposed_rubberband.append(pegs_inside[i])
                        temp_points += 1                        


            proposed_rubberband = list(set(proposed_rubberband))
        temp_points = len(proposed_rubberband)
        
        #print(player.rubberband_coordinates)
        #print(proposed_rubberband)

        for i in range(len(rubberband_edges)):
            if(rubberband_edges[i] not in player.peg_coordinates):
                illegal_move = True
                print("Given coordinates do not include your peg!")

        for i in range(len(proposed_rubberband)):
            if(proposed_rubberband[i] in players[other_player-1].peg_coordinates):
                if((cross_move and illegal_cross_move) or not cross_move):
                    print("Rubberband cannot go from an enemy peg!")
                    illegal_move = True
                else:
                    temp_points -= 1
            elif(proposed_rubberband[i] in player.rubberband_coordinates):
                temp_points -= 1
            else:
                temp_rubberband.append(proposed_rubberband[i])
        
        if(illegal_move):
            temp_points = 0
        else:
            for i in range(len(temp_rubberband)):
                player.rubberband_coordinates.append(temp_rubberband[i])
                if((temp_rubberband[i] not in player.peg_coordinates) and temp_rubberband[i] not in players[other_player-1].peg_coordinates):
                    player.board[temp_rubberband[i]] = player_index+2  # Alternates between Player 1 and Player 2 --- #3: g, 4:b\
            player.point += temp_points

        # Switch players after sweeping through all rubberband squares.
        player_index = 2
        other_player = 1

print("-----")
display_board(players[0].board, board_size[0], board_size[1])
print("-----")
display_board(players[1].board, board_size[0], board_size[1])
print("-----")
# Calculate and announce the winner
print(f"{players[0].name}: {players[0].point} points, {players[1].name}: {players[1].point} points")
if(players[0].point > players[1].point):
    print(f"{players[0].name} wins!")
elif(players[0].point < players[1].point):
    print(f"{players[1].name} wins!")
else:
    print(f"It is a tie! {players[0].name} started first, {players[0].name} wins!")

# Close the server and player sockets

server.close()
for player in players:
    player.socket.close()
