import visilibity as vis
from time import time

# Used in the create_cone function
import math

def testVisilibity():
    
    debut_timer_environnement = time()
    
    # Define an epsilon value (should be != 0.0)
    epsilon = 0.0000001
    
    # Create the outer boundary polygon
    walls = vis.Polygon([vis.Point(-1500,0), vis.Point(1500,0), vis.Point(1500,2000), vis.Point(-1500,2000)])
    
    # Define the point of the "observer"
    observer = vis.Point(1470,460)
    
    # Now we define some holes for our environment. The holes must be inside 
    # our outer boundary polygon. A hole blocks the observer vision, it works as
    # an obstacle in his vision sensor.
    
    # The smalles point should be first. The point of a hole must be in CLOCK-WISE(cw) order.
    
    hole = vis.Polygon([vis.Point(100, 300),vis.Point(100, 500),vis.Point(150, 500),vis.Point(150, 300)])
    hole1 = vis.Polygon([vis.Point(525, 875),vis.Point(525, 1125),vis.Point(775, 1125),vis.Point(775, 875)])
    hole2 = vis.Polygon([vis.Point(-775, 875),vis.Point(-775, 1125),vis.Point(-525, 1125),vis.Point(-525, 875)])
    
    # Create environment, wall will be the outer boundary because
    # is the first polygon in the list. The other polygons will be holes
    env = vis.Environment([walls, hole, hole1, hole2])
    
    # Check if the environment is valid
    print('Environment is valid : '+str(env.is_valid(epsilon)))
    
    
    # Define another point, could be used to check if the observer see it, to 
    # check the shortest path from one point to the other, etc.
    end = vis.Point(-1300, 1800)
    
    # Necesary to generate the visibility polygon
    observer.snap_to_boundary_of(env, epsilon)
    observer.snap_to_vertices_of(env, epsilon)
        
    debut_timer_path_finding = time()
    
    # Obtein the shortest path from 'observer' to 'end'
    # in the environment previously define
    shortest_path = env.shortest_path(observer, end, epsilon)
    
    # Print the length of the path
    print("Shortest Path length from observer to end: "+str(shortest_path.length()))

    print("############ CHEMIN ############")
    for i in range(shortest_path.size()):
        print(str(shortest_path[i]))
    
    print("################################")
    print("environnement chargé en "+str(debut_timer_path_finding - debut_timer_environnement)+" sec.")
    print("recherche de chemin chargée en "+str(time() - debut_timer_path_finding)+" sec.")

testVisilibity()
