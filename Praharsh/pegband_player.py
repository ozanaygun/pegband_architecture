import random
from collections import OrderedDict
from itertools import chain, combinations
from scipy.spatial import ConvexHull
from shapely.geometry import Point, Polygon
import math

def convexcheck(l,s):
    if(len(l)<3):
        return True
    points=[]
    for point in l:
        points.append([int(point%s),int(point/s)+1])
    
    try:
        ConvexHull(points)
        return True
    except Exception as e:
        return False

def make_convex(l,s):
    # Check if there are enough points to form a polygon
    if(len(l)<3):
        return l
    
    points=[]
    for point in l:
        points.append([int(point%s),int(point/s)+1])
    
    # Compute convex hull
    hull = ConvexHull(points)
    sorted_points = [points[i] for i in hull.vertices]

    # Find the center point
    center = tuple(map(sum, zip(*sorted_points)))  # center is the mean point
    center = (center[0] / len(sorted_points), center[1] / len(sorted_points))

    # Sort points in counterclockwise or clockwise order
    sorted_points.sort(key=lambda p: (180 + math.degrees(math.atan2(p[1] - center[1], p[0] - center[0]))) % 360)

    # Form the convex polygon
    convex_polygon = sorted_points
    out=[]
    for point in convex_polygon:
        out.append((point[1]-1)*s+point[0])
    return out
    
class PegbandPlayer:
    def __init__(self, name, board_length, board_width, board, num_pegs, num_rubberbands, player_color):
        self.name = "Praharsh"
        self.board_length = board_length
        self.board_width = board_width
        self.board = []
        self.num_pegs = num_pegs
        self.num_rubberbands = num_rubberbands
        self.player_color = player_color #1: G, first player -- 2: B, second player.
        self.peg_positions = []
        self.possibilities = []
        
    def checkvalidity(self, peg1, peg2):
        start_peg = min(peg1, peg2)
        end_peg = max(peg1, peg2)
        illegal_move=False
        
        x1 = int(start_peg% self.board_width )
        y1 = int(start_peg/self.board_length)+1
        x2 = int(end_peg%self.board_width)
        y2 = int(end_peg/self.board_length)+1

        positions = []  # List to store the positions the rubberband passes through

        vertical_diff = y1-y2
        horizontal_diff = x1-x2
        
        # Check if there is any enemy pegs in between for cross move
        for i in range(len(self.board)):
            if((self.player_color==2 and self.board[i]==1) or(self.player_color==1 and self.board[i]==2)):
                cur_x = int(i%self.board_length)
                cur_y = int(i/self.board_length)+1
                # Line equation between pegs, check if it goes from any of the enemy pegs, illegal move.
                if(horizontal_diff!=0):
                    slope = vertical_diff/horizontal_diff
                    if((cur_x - x1)*slope == (cur_y - y1)):
                        illegal_move = True
                else:
                    if(cur_x==x1):
                        illegal_move = True
        
        if(illegal_move):
            return False
        else:
            return True

    def checkopp(self,l):
        points=[]
        for point in l:
            points.append(Point(int(point%self.board_length),int(point/self.board_length)+1))
        pol=Polygon(points)
        print(points)
        for i in range(self.board_length*self.board_width):
            if(((self.board[i]==2 and self.player_color==1) or (self.board[i]==1 and self.player_color==2)) 
               and (pol.contains(Point(int(i%self.board_length),int(i/self.board_length)+1)) or Point(int(i%self.board_length),int(i/self.board_length)+1).intersects(pol.boundary))):
                return True
        
        return False
    
    def place_pegs(self):
        print("placing pegs")
        position = 0
        cur_max=0
        cur_dist=abs(math.dist([0,0],[self.board_length/2,self.board_length/2]))
        for i in range(self.board_length*self.board_width):
            print("position currently is")
            print(position,cur_dist,cur_max)
            if(self.board[i]==1 or self.board[i]==2):
                continue
            count=0
            for j in range(self.board_length*self.board_width):
                if((self.board[j]==2 and self.player_color==1) or (self.board[j]==2 and self.player_color==1)):
                    continue
                if(self.checkvalidity(i,j)):
                    if((self.board[j]==1 and self.player_color==1) or (self.board[j]==2 and self.player_color==2)):
                        count=count+math.dist([int(i%self.board_length),int(i/self.board_length)+1] ,[int(j%self.board_length),int(j/self.board_length)+1])
                    count=count+1
            
            if(count>cur_max):
                position=i
                x1 = int(i% self.board_width )
                y1 = int(i/self.board_length)+1
                cur_max=count
                cur_dist=abs(math.dist([x1,y1],[self.board_length/2,self.board_length/2]))
            elif(count==cur_max):
                x1 = int(i% self.board_width )
                y1 = int(i/self.board_length)+1
                if(cur_dist>math.dist([x1,y1],[self.board_length/2,self.board_length/2])):
                    position=i
                    cur_dist=math.dist([x1,y1],[self.board_length/2,self.board_length/2])
        self.peg_positions.append(position)
        print(position)
        return position
        
    
    def place_rubberbands(self):
        # Fill this function to return your move to place your rubberbands to the pegs
        for sublist in reversed(self.possibilities):
            if(convexcheck(list(sublist),self.board_length)):
                list1=make_convex(list(sublist),self.board_length)
                if(self.checkopp(list1)):
                    self.possibilities.remove(sublist)
                    continue   
                print(list1)
                return list1
            else:
                self.possibilities.remove(sublist)
    
    def calc_possibilities(self):
        self.possibilities= list(chain(*map(lambda x: combinations(self.peg_positions, x), range(1, len(self.peg_positions)+1))))
        
                

