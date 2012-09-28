# -*- coding: utf-8 -*-

import visilibity as vis
import time

# Used in the create_cone function
import math

def testVisilibity():
    
    debut_timer_environnement = time.time()
    
    # Define an epsilon value (should be != 0.0)
    epsilon = 0.0000001
    
    # Define the points which will be the outer boundary of the environment
    # Must be COUNTER-CLOCK-WISE(ccw)
    p1 = vis.Point(-1500,0)
    p2 = vis.Point(1500,0)
    p3 = vis.Point(1500,2000)
    p4 = vis.Point(-1500,2000)
    
    # Load the values of the outer boundary polygon in order to draw it later
    wall_x = [p1.x, p2.x, p3.x, p4.x, p1.x]
    wall_y = [p1.y, p2.y, p3.y, p4.y, p1.y]
    
    # Outer boundary polygon must be COUNTER-CLOCK-WISE(ccw)
    # Create the outer boundary polygon
    walls = vis.Polygon([p1, p2, p3, p4])
    
    # Define the point of the "observer"
    observer = vis.Point(1470,460)
    
    # Uncomment the following line in order to create a cone polygon
    #walls = create_cone((observer.x, observer.y), 500, 270, 30, quality= 3)
    
    # Walls should be in standard form
    print 'Walls in standard form : ',walls.is_in_standard_form()
    
    # Now we define some holes for our environment. The holes must be inside 
    # our outer boundary polygon. A hole blocks the observer vision, it works as
    # an obstacle in his vision sensor.
    
    
    # We define some point for a hole. You can add more points in order to get
    # the shape you want.
    # The smalles point should be first
    p2 =vis.Point(100, 300)
    p3 =vis.Point(100, 500)
    p4 =vis.Point(150, 500)
    p1 =vis.Point(150, 300)
    
    # Load the values of the hole polygon in order to draw it later
    hole_x = [p1.x, p2.x, p3.x, p4.x,p1.x]
    hole_y = [p1.y, p2.y, p3.y, p4.y,p1.y]
    
    # Note: The point of a hole must be in CLOCK-WISE(cw) order.
    # Create the hole polygon
    hole = vis.Polygon([p2,p3,p4,p1])
    
    # Check if the hole is in standard form
    print 'Hole in standard form: ',hole.is_in_standard_form()
    
    
    # Define another point of a hole polygon
    # Remember: the list of points must be CLOCK-WISE(cw)
    p1 =vis.Point(525, 875)
    p2 =vis.Point(525, 1125)
    p3 =vis.Point(775, 1125)
    p4 =vis.Point(775, 875)
    
    # Load the values of the hole polygon in order to draw it later
    hole1_x = [p1.x, p2.x, p3.x, p4.x,p1.x]
    hole1_y = [p1.y, p2.y, p3.y, p4.y,p1.y]
    
    # Create the hole polygon
    hole1 = vis.Polygon([p1,p2,p3,p4])
    
    # Check if the hole is in standard form
    print 'Hole in standard form: ',hole1.is_in_standard_form()

    # Define another point of a hole polygon
    # Remember: the list of points must be CLOCK-WISE(cw)    
    p2 =vis.Point(-775, 875)
    p3 =vis.Point(-775, 1125)
    p4 =vis.Point(-525, 1125)
    p1 =vis.Point(-525, 875)
    
    # Load the values of the hole polygon in order to draw it later
    hole2_x = [p1.x, p2.x, p3.x, p4.x,p1.x]
    hole2_y = [p1.y, p2.y, p3.y, p4.y,p1.y]
    
    # Create the hole polygon
    hole2 = vis.Polygon([p2,p3,p4,p1])
    
    # Check if the hole is in standard form
    print 'Hole in standard form: ',hole2.is_in_standard_form()
    
    # Define another point of a hole polygon
    # Remember: the list of points must be CLOCK-WISE(cw)    
    p1 =vis.Point(1100, 500)
    p2 =vis.Point(1100, 518)
    p3 =vis.Point(1500, 518)
    p4 =vis.Point(1500, 500)
    
    # Load the values of the hole polygon in order to draw it later
    hole3_x = [p1.x, p2.x, p3.x, p4.x,p1.x]
    hole3_y = [p1.y, p2.y, p3.y, p4.y,p1.y]
    
    # Create the hole polygon
    hole3 = vis.Polygon([p1,p2,p3,p4])
    
    # Check if the hole is in standard form
    print 'Hole in standard form: ',hole3.is_in_standard_form()
    
    # Define another point of a hole polygon
    # Remember: the list of points must be CLOCK-WISE(cw)    
    p1 =vis.Point(-1500, 500)
    p2 =vis.Point(-1500, 518)
    p3 =vis.Point(-1100, 518)
    p4 =vis.Point(-1100, 500)
    
    # Load the values of the hole polygon in order to draw it later
    hole4_x = [p1.x, p2.x, p3.x, p4.x,p1.x]
    hole4_y = [p1.y, p2.y, p3.y, p4.y,p1.y]
    
    # Create the hole polygon
    hole4 = vis.Polygon([p1,p2,p3,p4])
    
    # Check if the hole is in standard form
    print 'Hole in standard form: ',hole4.is_in_standard_form()
    
     # Define another point of a hole polygon
    # Remember: the list of points must be CLOCK-WISE(cw)    
    p1 =vis.Point(1115, 1270)
    p2 =vis.Point(1160, 1998)
    p3 =vis.Point(1175, 1998)
    p4 =vis.Point(1130, 1270)
    
    # Load the values of the hole polygon in order to draw it later
    hole5_x = [p1.x, p2.x, p3.x, p4.x,p1.x]
    hole5_y = [p1.y, p2.y, p3.y, p4.y,p1.y]
    
    # Create the hole polygon
    hole5 = vis.Polygon([p1,p2,p3,p4])
    
    # Check if the hole is in standard form
    print 'Hole in standard form: ',hole5.is_in_standard_form()
    
     # Define another point of a hole polygon
    # Remember: the list of points must be CLOCK-WISE(cw)    
    p1 =vis.Point(-1130, 1270)
    p2 =vis.Point(-1175, 1998)
    p3 =vis.Point(-1160, 1998)
    p4 =vis.Point(-1115, 1270)
    
    # Load the values of the hole polygon in order to draw it later
    hole6_x = [p1.x, p2.x, p3.x, p4.x,p1.x]
    hole6_y = [p1.y, p2.y, p3.y, p4.y,p1.y]
    
    # Create the hole polygon
    hole6 = vis.Polygon([p1,p2,p3,p4])
    
    # Check if the hole is in standard form
    print 'Hole in standard form: ',hole6.is_in_standard_form()
    
    
    # Create environment, wall will be the outer boundary because
    # is the first polygon in the list. The other polygons will be holes
    env = vis.Environment([walls, hole,hole2, hole1, hole3, hole4, hole5, hole6])
    
    
    # Check if the environment is valid
    print 'Environment is valid : ',env.is_valid(epsilon)
    
    
    # Define another point, could be used to check if the observer see it, to 
    # check the shortest path from one point to the other, etc.
    end = vis.Point(-1300, 1800)
    
    # Necesary to generate the visibility polygon
    observer.snap_to_boundary_of(env, epsilon)
    observer.snap_to_vertices_of(env, epsilon)
        
    # Obtein the visibility polygon of the 'observer' in the environmente
    # previously define
    isovist = vis.Visibility_Polygon(observer, env, epsilon)
    
    debut_timer_path_finding = time.time()
    
    # Uncomment the following line to obtein the visibility polygon 
    # of 'end' in the environmente previously define
    #polygon_vis = vis.Visibility_Polygon(end, env, epsilon)
    
    # Obtein the shortest path from 'observer' to 'end'
    # in the environment previously define
    shortest_path = env.shortest_path(observer, end, epsilon)
    
    # Print the length of the path
    print "Shortest Path length from observer to end: ", shortest_path.length()
    
    
    # Print the point of the visibility polygon of 'observer' and save them 
    # in two arrays in order to draw the polygon later
    point_x , point_y  = save_print(isovist)
    
    # Add the first point again because the function to draw, draw a line from
    # one point to the next one and to close the figure we need the last line
    # from the last point to the first one
    point_x.append(isovist[0].x)
    point_y.append(isovist[0].y)    

    print "##########################################"
    for i in range(shortest_path.size()):
        print shortest_path[i]
        
    
    print "##########################################"
    print "environnement chargé en "+str(debut_timer_path_finding - debut_timer_environnement)+" sec."
    print "recherche de chemin chargée en "+str(time.time() - debut_timer_path_finding)+" sec."
    

def save_print(polygon):
    end_pos_x = []
    end_pos_y = []
    print 'Points of Polygon: '
    for i in range(polygon.n()):
        x = polygon[i].x
        y = polygon[i].y
        
        end_pos_x.append(x)
        end_pos_y.append(y)
                
        print x,y 
        
    return end_pos_x, end_pos_y 


if __name__ == "__main__":
    testVisilibity()
