
from sklearn.cluster import KMeans
import numpy as np
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import math
import random

class solution():
    def __init__(self, vertices) -> None:
        self.vertices = vertices
        self.area = Polygon(vertices).area if len(vertices) > 2 else man_dist(vertices[0][0], vertices[0][1], vertices[1][0], vertices[1][1])

TWO_PI = 2 * math.pi

def is_convex_polygon(polygon):
    """Return True if the polynomial defined by the sequence of 2D
    points is 'strictly convex': points are valid, side lengths non-
    zero, interior angles are strictly between zero and a straight
    angle, and the polygon does not intersect itself.

    NOTES:  1.  Algorithm: the signed changes of the direction angles
                from one side to the next side must be all positive or
                all negative, and their sum must equal plus-or-minus
                one full turn (2 pi radians). Also check for too few,
                invalid, or repeated points.
            2.  No check is explicitly done for zero internal angles
                (180 degree direction-change angle) as this is covered
                in other ways, including the `n < 3` check.
    """
    try:  # needed for any bad points or direction changes
        # Check for too few points
        if len(polygon) < 3:
            return False
        # Get starting information
        old_x, old_y = polygon[-2]
        new_x, new_y = polygon[-1]
        new_direction = math.atan2(new_y - old_y, new_x - old_x)
        angle_sum = 0.0
        # Check each point (the side ending there, its angle) and accum. angles
        for ndx, newpoint in enumerate(polygon):
            # Update point coordinates and side directions, check side length
            old_x, old_y, old_direction = new_x, new_y, new_direction
            new_x, new_y = newpoint
            new_direction = math.atan2(new_y - old_y, new_x - old_x)
            if old_x == new_x and old_y == new_y:
                return False  # repeated consecutive points
            # Calculate & check the normalized direction-change angle
            angle = new_direction - old_direction
            if angle <= -math.pi:
                angle += TWO_PI  # make it in half-open interval (-Pi, Pi]
            elif angle > math.pi:
                angle -= TWO_PI
            if ndx == 0:  # if first time through loop, initialize orientation
                if angle == 0.0:
                    return False
                orientation = 1.0 if angle > 0.0 else -1.0
            else:  # if other time through loop, check orientation is stable
                if orientation * angle <= 0.0:  # not both pos. or both neg.
                    return False
            # Accumulate the direction-change angle
            angle_sum += angle
        # Check that the total number of full turns is plus-or-minus 1
        return abs(round(angle_sum / TWO_PI)) == 1
    except (ArithmeticError, TypeError, ValueError):
        return False  # any exception means not a proper convex polygon

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
        self.solutions = None

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
                x_ = self.board_length - 1 - new_enemy_peg[0]
                y_ = self.board_length - 1 - new_enemy_peg[1]
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
                x_ = self.board_length - 1 - new_enemy_peg[0]
                y_ = self.board_length - 1 - new_enemy_peg[1]
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
        if self.solutions is None:
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
                                valid_edges.append([(i[0], i[1]), (j[0], j[1])]) # edge of form [(x1, y1), (x2, y2)]
                
                N = len(my_pegs)

                prev_nth_poly = []

                for i in valid_edges:
                    prev_nth_poly.append(solution(i))

                best_solutions = []

                best_solutions.extend(prev_nth_poly[:N])
                print(len(best_solutions))

                for i in range(3, N+1):
                    n_th_poly = []
                    for prev_poly in prev_nth_poly:
                        for peg in my_pegs:
                            new_vertices = []
                            for ver in prev_poly.vertices:
                                new_vertices.append(ver)
                            new_vertices.append(peg)
                            new_poly = solution(new_vertices)
                            if not is_convex_polygon(new_poly):
                                continue
                            else:
                                n_th_poly.append(new_poly)
                    best_solutions.extend(n_th_poly[:N])
                    print(len(best_solutions))
                    prev_nth_poly = n_th_poly

                best_solutions.sort(key=lambda t : t.area)
                self.solutions = best_solutions

                my = self.solutions.pop(0)
                result = []
                for i in my.vertices:
                    result.append(i[0] + i[1] * self.board_length)
                print(result, len(self.solutions))
                return result
            else:
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
                                valid_edges.append([(i[0], i[1]), (j[0], j[1])]) # edge of form [(x1, y1), (x2, y2)]
                
                N = len(my_pegs)

                prev_nth_poly = []

                for i in valid_edges:
                    prev_nth_poly.append(solution(i))

                best_solutions = []

                best_solutions.extend(prev_nth_poly[:N])

                for i in range(3, N+1):
                    n_th_poly = []
                    for prev_poly in prev_nth_poly:
                        for peg in my_pegs:
                            new_vertices = []
                            for ver in prev_poly.vertices:
                                new_vertices.append(ver)
                            new_vertices.append(peg)
                            new_poly = solution(new_vertices)
                            if not is_convex_polygon(new_poly):
                                continue
                            else:
                                n_th_poly.append(new_poly)
                    best_solutions.extend(n_th_poly[:N])
                    prev_nth_poly = n_th_poly

                best_solutions.sort(key=lambda t : t.area)
                self.solutions = best_solutions

                my = self.solutions.pop(0)
                result = []
                for i in my.vertices:
                    result.append(i[0] + i[1] * self.board_length)
                print(result, len(self.solutions))
                return result
        
        else:
            my = self.solutions.pop(0)
            result = []
            for i in my.vertices:
                result.append(i[0] + i[1] * self.board_length)
            print(result, len(self.solutions))
            return result