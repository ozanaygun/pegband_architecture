import random
import numpy as np
import math

class Point:
  x: int | float
  y: int | float
  def __init__(self, x: int | float, y: int | float):
    self.x = x
    self.y = y

  def __str__(self):
    return "({}, {})".format(self.x, self.y)

  def __repr__(self):
    return "({}, {})".format(self.x, self.y)
  
  def flatten(self, N: int) -> int | float:
    return self.x * N + self.y

class Triangle:
  p0: Point
  p1: Point
  p2: Point
  sign: int | None
  A: int | None
  def __init__(self, p0: Point, p1: Point, p2: Point):
    self.p0 = p0
    self.p1 = p1
    self.p2 = p2
    self.sign = None

  def isPointInside(self, p: Point, include_edge: bool = True) -> bool:
    if self.sign == None:
      self.A = 1/2 * (-self.p1.y * self.p2.x + self.p0.y * (-self.p1.x + self.p2.x) + self.p0.x * (self.p1.y - self.p2.y) + self.p1.x * self.p2.y)
      self.sign = -1 if self.A < 0 else 1
    s = (self.p0.y * self.p2.x - self.p0.x * self.p2.y + (self.p2.y - self.p0.y) * p.x + (self.p0.x - self.p2.x) * p.y) * self.sign
    t = (self.p0.x * self.p1.y - self.p0.y * self.p1.x + (self.p0.y - self.p1.y) * p.x + (self.p1.x - self.p0.x) * p.y) * self.sign
    if include_edge:
      return s >= 0 and t >= 0 and (s + t) <= 2 * self.A * self.sign
    else:
      return s > 0 and t > 0 and (s + t) < 2 * self.A * self.sign
  
  def getEstimatedArea(self) -> int:
    x0 = min(self.p0.x, self.p1.x, self.p2.x)
    x1 = max(self.p0.x, self.p1.x, self.p2.x)
    y0 = min(self.p0.y, self.p1.y, self.p2.y)
    y1 = max(self.p0.y, self.p1.y, self.p2.y)
    return (x1 - x0 + 2) * (y1 - y0 + 2) // 2 - 2

  def getArea(self, claimed_map: np.ndarray) -> int:
    x0 = min(self.p0.x, self.p1.x, self.p2.x)
    x1 = max(self.p0.x, self.p1.x, self.p2.x)
    y0 = min(self.p0.y, self.p1.y, self.p2.y)
    y1 = max(self.p0.y, self.p1.y, self.p2.y)
    result = Line(self.p0, self.p1).getArea() + Line(self.p1, self.p2).getArea() + Line(self.p2, self.p0).getArea() - 3
    for i in range(x0, x1 + 1):
      for j in range(y0, y1 + 1):
        if claimed_map[i][j] == True and self.isPointInside(Point(i, j), False):
          result += 1
    return result

  def __str__(self):
    return "[{} {} {}]".format(self.p0, self.p1, self.p2)

  def __repr__(self):
    return "[{} {} {}]".format(self.p0, self.p1, self.p2)

class Line:
  p0: Point
  p1: Point

  def __init__(self, p0: Point, p1: Point) -> None:
    self.p0 = p0
    self.p1 = p1
  
  def getArea(self) -> int:
    return 1 + abs(self.p0.x - self.p1.x) + abs(self.p0.y - self.p1.y)

class Board:
  board: np.ndarray
  N: int
  side: int
  points: tuple[list[int]]
  claimed_map: np.ndarray

  def __init__(self, board_array: list[int], N: int, side):
    self.board = np.ndarray((N, N), dtype=int)
    self.claimed_map = np.ndarray((N, N), dtype=bool)
    self.N = N
    self.side = side
    for i in range(0, N):
      for j in range(0, N):
        self.board[i][j] = board_array[i * N + j]
    self.points= ([], [])
    for i in range(0, self.N):
      for j in range(0, self.N):
        self.claimed_map[i][j] = False
        if self.board[i][j] == side + 1:
          self.points[side].append(Point(i, j))
        elif self.board[i][j] == 2 - side:
          self.points[1 - side].append(Point(i, j))
          self.claimed_map[i][j] = True
        elif self.board[i][j] == side + 2:
          self.claimed_map[i][j] = True
  
  def getAllTriangles(self, side = None):
    if side == None:
      side = self.side
    for p0 in range(0, len(self.points[side])):
      for p1 in range(p0 + 1, len(self.points[side])):
        for p2 in range(p1 + 1, len(self.points[side])):
          triangle: Triangle = Triangle(self.points[side][p0], self.points[side][p1], self.points[side][p2])
          blocked = False
          for p in range(0, len(self.points[1 - side])):
            if triangle.isPointInside(self.points[1 - side][p]):
              blocked = True
              break
          if not blocked:
            yield triangle
  
  def getBestPoint(self, eval_all) -> Point:
    val = 0
    best_point = []
    for i in range(0, self.N):
      for j in range(0, self.N):
        if self.board[i][j] != 0:
          continue
        new_val = eval_all(Point(i, j))
        if new_val > val:
          val = new_val
          best_point = [Point(i, j)]
        elif new_val == val:
          best_point.append(Point(i, j))
    if len(best_point) == 0:
      return Point(random.randint(0, self.N - 1), random.randint(0, self.N - 1))
    return random.choice(best_point)

class PegbandPlayer:
  def __init__(self, board_width, peg_count, band_count, player_color):
    self.N = board_width
    self.peg_count = peg_count
    self.band_count = band_count
    self.side = player_color - 1 #1: G, first player -- 2: B, second player.

  def placePegs(self, round_count: int, board_array: list[int]):
    # Fill this function to return your move to place a peg to the board
    board = Board(board_array, self.N, self.side)
    
    if round_count == 0:
      def eval_all(p: Point):
        return p.x == 0 or p.x == self.N - 1 or p.y == 0 or p.y == self.N - 1
    else:
      def eval_constructivity(p: Point):
        result = 0
        for peg in board.points[self.side]:
          if peg.x != p.x and peg.y != p.y and math.gcd(abs(peg.x - p.x), abs(peg.y - p.y)) == 1:
            result += (self.peg_count - round_count) + (abs(peg.x - p.x) + abs(peg.y - p.y))
          else:
            blocked = False
            for enemy_peg in board.points[1 - self.side]:
              if abs(enemy_peg.x - p.x) * abs(peg.y - p.y) == abs(enemy_peg.y - p.y) * abs(peg.x - p.x):
                blocked = True
                break
            if blocked == False:
              result += 1
        return result
      if round_count < 3 - self.side:
        def eval_all(p: Point):
          return eval_constructivity(p)
      elif round_count < 0.8 * self.peg_count:
        def eval_all(p: Point):
          result = 0
          for triangle in board.getAllTriangles(1 - self.side):
            if triangle.isPointInside(p):
              result += 1
          return result * 80 + eval_constructivity(p)
      else:
        def eval_all(p: Point):
          result = 0
          for triangle in board.getAllTriangles(1 - self.side):
            if triangle.isPointInside(p):
              result += triangle.getEstimatedArea() + 1
          return result * 6 + eval_constructivity(p)
    return board.getBestPoint(eval_all).flatten(self.N)
  
  def placeBands(self, round_count: int, board_array: list[int]):
    # Fill this function to return your move to place your rubberbands to the pegs
    board = Board(board_array, self.N, self.side)
    triangles = list(board.getAllTriangles())
    triangles.sort(key = lambda triangle: -triangle.getArea(board.claimed_map))
    if len(triangles):
      return [triangles[0].p0.flatten(self.N), triangles[0].p1.flatten(self.N), triangles[0].p2.flatten(self.N)]
    else:
      return [board.points[self.side][random.randint(0, self.peg_count)].flatten(self.N), board.points[self.side][random.randint(0, self.peg_count)].flatten(self.N)]