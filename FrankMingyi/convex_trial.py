import matplotlib.path as mpath
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
from shapely.ops import cascaded_union

# Define the coordinates of the k points that form the convex polygon
pegs = [16, 48, 39, 30]
points = []
board_size = 8

for i in range(len(pegs)):
    x1 = (int(pegs[i]%board_size) + 0.5) 
    y1 = -1*(int(pegs[i]/board_size)+1 - 0.5 - board_size)
    points.append([x1, y1])
x1 = int(pegs[0]%board_size) + 0.5 
y1 = -1*(int(pegs[0]/board_size)+1 - 0.5 - board_size)
points.append([x1, y1])

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

# Expand the polygon
expanded_points = expand_polygon(points)

# Check convexity
if is_convex(expanded_points):
    print("The polygon is convex.")
else:
    print("The polygon is not convex.")

# Define the grid size
grid_size = board_size

# Create a list of grid centers
grid_centers = [[0.5 + x, 0.5 + y] for y in range(grid_size) for x in range(grid_size)]

# Create a Path object from the expanded polygon points
path = mpath.Path(expanded_points)

# Initialize a list to store the grid centers inside the polygon
grid_centers_inside_polygon = []
center_locations_inside_polygon = []

# Check each grid center if it's inside the polygon
for center in grid_centers:
    if path.contains_point(center):
        if center not in points:
            grid_centers_inside_polygon.append(center)
            center_locations_inside_polygon.append(int((center[1]*(-1) + board_size + 0.5 - 1)*(board_size) + (center[0] - 0.5)))

# Print the grid centers inside the polygon
print("Grid centers inside the polygon:")
for center in grid_centers_inside_polygon:
    print(center)

print(center_locations_inside_polygon)

# Plot the polygon and the grid centers
x, y = zip(*expanded_points)
plt.plot(x, y, 'bo-')
x, y = zip(*grid_centers)
plt.plot(x, y, 'ro')
if(grid_centers_inside_polygon != []):
    x, y = zip(*grid_centers_inside_polygon)
    plt.plot(x, y, 'go')
plt.gca().set_aspect('equal', adjustable='box')
plt.show()
