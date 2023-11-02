
from sklearn.cluster import KMeans
import numpy as np
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import math
import random

def distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def point_on_line(p1, p2, p3):
    # returns true if p3 is on line formed by p1 and p2. p is a tuple of (x, y)
    return math.isclose(distance(p1,p3) + distance(p2,p3), distance(p1,p2))


def man_dist(x1, y1, x2, y2):
    return abs(x1 - x2) + abs(y1 - y2)

class PegbandPlayer:
    def __init__(self, name, board_length, board_width, board, num_pegs, num_rubberbands, player_color):
        self.name = "Julian"
        self.board_length = board_length
        self.board_width = board_width
        self.board = []
        self.num_pegs = num_pegs
        self.num_rubberbands = num_rubberbands
        self.player_color = player_color #1: G, first player -- 2: B, second player.
        self.peg_positions = []
        self.enemy_pegs = []

    def place_pegs(self):
        # Fill this function to return your move to place a peg to the board
        # list of enemy pegs
        size = self.board_length
        #print(self.player_color == 1)
        their_pegs = []

        if self.player_color == 1:
            # player 1
            for i in range(len(self.board)):
                if self.board[i] == 2: # 2 for player 2's peg
                    x = i % size
                    y = i // size
                    their_pegs.append((x,y)) # x, y range [0, size-1]

            new_enemy_peg = None
            for i in their_pegs:
                if i not in self.enemy_pegs:
                    new_enemy_peg = i
                    break
            self.enemy_pegs = their_pegs

            # if first move, place at center
            # elif move is mid or end, place kmeans
            # else mirror
            if new_enemy_peg is None:
                # first move
                return len(self.board) // 2 + self.board_length // 2
            elif len(their_pegs) == self.num_pegs - 1 or len(their_pegs) == self.num_pegs // 2 - 1:
                # mid or end, kmeans
                X = np.array(their_pegs)
                kmeans = KMeans(n_clusters=1).fit(X)
                center = kmeans.cluster_centers_[0]
                x_ = int(center[0])
                y_ = int(center[1])
                if self.board[y_ * self.board_length + x_] == 0:
                    return y_ * self.board_length + x_
                else:
                    if y_ * self.board_length + x_ + 1 < len(self.board) and self.board[y_ * self.board_length + x_ + 1] == 0:
                        return y_ * self.board_length + x_ + 1
                    if y_ * self.board_length + x_ + 1 < len(self.board) and self.board[(y_ + 1) * self.board_length + x_] == 0:
                        return (y_ + 1) * self.board_length + x_
                    if y_ * self.board_length + x_ + 1 < len(self.board) and self.board[(y_ + 1) * self.board_length + x_ + 1] == 0:
                        return (y_ + 1) * self.board_length + x_ + 1
                    return 0
            else:
                x_ = self.board_length - new_enemy_peg[0]
                y_ = self.board_length - new_enemy_peg[1]
                if self.board[y_ * self.board_length + x_] == 0:
                    return y_ * self.board_length + x_
                else:
                    if y_ * self.board_length + x_ + 1 < len(self.board) and self.board[y_ * self.board_length + x_ + 1] == 0:
                        return y_ * self.board_length + x_ + 1
                    if y_ * self.board_length + x_ + 1 < len(self.board) and self.board[(y_ + 1) * self.board_length + x_] == 0:
                        return (y_ + 1) * self.board_length + x_
                    if y_ * self.board_length + x_ + 1 < len(self.board) and self.board[(y_ + 1) * self.board_length + x_ + 1] == 0:
                        return (y_ + 1) * self.board_length + x_ + 1
                    return 0
        else:
            # player 2
            for i in range(len(self.board)):
                if self.board[i] == 1: # 1 for player 1's peg
                    x = i % size
                    y = i // size
                    their_pegs.append((x,y)) # x, y range [0, size-1]

            new_enemy_peg = None
            for i in their_pegs:
                if i not in self.enemy_pegs:
                    new_enemy_peg = i
                    break
            self.enemy_pegs = their_pegs
            # if move is mid or end, place kmeans
            # else mirror

            if len(their_pegs) == self.num_pegs or len(their_pegs) == self.num_pegs // 2:
                X = np.array(their_pegs)
                kmeans = KMeans(n_clusters=1).fit(X)
                center = kmeans.cluster_centers_[0]
                x_ = int(center[0])
                y_ = int(center[1])
                if self.board[y_ * self.board_length + x_] == 0:
                    return y_ * self.board_length + x_
                else:
                    if y_ * self.board_length + x_ + 1 < len(self.board) and self.board[y_ * self.board_length + x_ + 1] == 0:
                        return y_ * self.board_length + x_ + 1
                    if y_ * self.board_length + x_ + 1 < len(self.board) and self.board[(y_ + 1) * self.board_length + x_] == 0:
                        return (y_ + 1) * self.board_length + x_
                    if y_ * self.board_length + x_ + 1 < len(self.board) and self.board[(y_ + 1) * self.board_length + x_ + 1] == 0:
                        return (y_ + 1) * self.board_length + x_ + 1
                    return 0
            else:
                x_ = self.board_length - new_enemy_peg[0]
                y_ = self.board_length - new_enemy_peg[1]
                if self.board[y_ * self.board_length + x_] == 0:
                    return y_ * self.board_length + x_
                else:
                    if y_ * self.board_length + x_ + 1 < len(self.board) and self.board[y_ * self.board_length + x_ + 1] == 0:
                        return y_ * self.board_length + x_ + 1
                    if y_ * self.board_length + x_ + 1 < len(self.board) and self.board[(y_ + 1) * self.board_length + x_] == 0:
                        return (y_ + 1) * self.board_length + x_
                    if y_ * self.board_length + x_ + 1 < len(self.board) and self.board[(y_ + 1) * self.board_length + x_ + 1] == 0:
                        return (y_ + 1) * self.board_length + x_ + 1
                    return 0


    def place_rubberbands(self):
        # Fill this function to return your move to place your rubberbands to the pegs
        # first make list of possible edges
        # then make list of possible triangles
        # then return whatever has the greatest edge length sum
        '''
        point = Point(-0.5, 0.5)
        polygon = Polygon([(0, 0), (0, 1), (1, 1), (1, 0)])
        print(polygon.contains(point))  
        '''
        size = self.board_length
        my_pegs = [] # my pegs in (x, y)
        points = [] # my pegs in point class
        their_pegs = [] # their pegs in (x, y)
        if self.player_color == 1:
            # player 1
            for i in range(len(self.board)):
                if self.board[i] == 1:
                    x = i % size
                    y = i // size
                    my_pegs.append((x, y))
            
            for i in my_pegs:
                point = Point(i[0], i[1])
                points.append(point)

            valid_edges = []

            for i in range(len(self.board)):
                if self.board[i] == 2: # 2 for player 2's peg
                    x = i % size
                    y = i // size
                    their_pegs.append((x,y)) # x, y range [0, size-1]

            # all edges
            for i in my_pegs:
                for j in my_pegs:
                    if i == j:
                        continue
                    for k in their_pegs:
                        if point_on_line(i, j, k):
                            continue
                        else:
                            valid_edges.append((i[0], i[1], j[0], j[1])) # edge of form (x1, y1, x2, y2)
            
            valid_triangle = []

            their_points = []
            for i in their_pegs:
                their_points.append(Point(i[0], i[1]))

            for edge in valid_edges:
                for i in my_pegs:
                    if i[0] == edge[0] and i[1] == edge[1]:
                        continue
                    elif i[0] == edge[2] and i[1] == edge[3]:
                        continue
                    else:
                        valid_tri = True
                        for k in their_points:
                            poly_triangle = Polygon([(edge[0], edge[1]), (edge[2], edge[3]), (i[0], i[1])])
                            if poly_triangle.contains(k):
                                valid_tri = False
                                break
                        if valid_tri:
                            valid_triangle.append((edge[0], edge[1], edge[2], edge[3], i[0], i[1])) # form (x1, y1, x2, y2, x3, y3) three points triangle
            
            valid_triangle.sort(key=lambda t : man_dist(t[0], t[1], t[2], t[3]) + man_dist(t[0], t[1], t[4], t[5]) + man_dist(t[2], t[3], t[4], t[5]))
            print(len(valid_triangle))
            if len(valid_triangle) > 50:
                valid_triangle = valid_triangle[:30]

            result = random.choice(valid_triangle)
            rubber_band = []
            rubber_band.append(result[0] + result[1] * size)
            rubber_band.append(result[2] + result[3] * size)
            rubber_band.append(result[4] + result[5] * size)
            print(rubber_band)
            return rubber_band
            

        else:
            # player 2
            for i in range(len(self.board)):
                if self.board[i] == 2:
                    x = i % size
                    y = i // size
                    my_pegs.append((x, y))
            
            for i in my_pegs:
                point = Point(i[0], i[1])
                points.append(point)

            valid_edges = []

            for i in range(len(self.board)):
                if self.board[i] == 1: # 1 for player 1's peg
                    x = i % size
                    y = i // size
                    their_pegs.append((x,y)) # x, y range [0, size-1]
            # all edges
            for i in my_pegs:
                for j in my_pegs:
                    if i == j:
                        continue
                    for k in their_pegs:
                        if point_on_line(i, j, k):
                            continue
                        else:
                            valid_edges.append((i[0], i[1], j[0], j[1])) # edge of form (x1, y1, x2, y2)
            
            valid_triangle = []

            their_points = []
            for i in their_pegs:
                their_points.append(Point(i[0], i[1]))

            for edge in valid_edges:
                for i in my_pegs:
                    if i[0] == edge[0] and i[1] == edge[1]:
                        continue
                    elif i[0] == edge[2] and i[1] == edge[3]:
                        continue
                    else:
                        valid_tri = True
                        for k in their_points:
                            poly_triangle = Polygon([(edge[0], edge[1]), (edge[2], edge[3]), (i[0], i[1])])
                            if poly_triangle.contains(k):
                                valid_tri = False
                                break
                        if valid_tri:
                            valid_triangle.append((edge[0], edge[1], edge[2], edge[3], i[0], i[1])) # form (x1, y1, x2, y2, x3, y3) three points triangle
            
            valid_triangle.sort(key=lambda t : man_dist(t[0], t[1], t[2], t[3]) + man_dist(t[0], t[1], t[4], t[5]) + man_dist(t[2], t[3], t[4], t[5]))
            print(len(valid_triangle))
            if len(valid_triangle) > 50:
                valid_triangle = valid_triangle[:30]

            result = random.choice(valid_triangle)
            rubber_band = []
            rubber_band.append(result[0] + result[1] * size)
            rubber_band.append(result[2] + result[3] * size)
            rubber_band.append(result[4] + result[5] * size)
            print(rubber_band)
            return rubber_band