#ifndef POLYGON_H
#define POLYGON_H

#include "visilibity.hpp"
#include "table.h"

class VisilibityWrapper
{  
public:
    enum Exception
    {
        RETURN_OK,
        ENVIRONMENT_IS_NOT_VALID
    };

public:
    VisilibityWrapper(int width, int height, int ratio);
    void tolerance_cv(double t);
    void epsilon_vis(double e);
    void add_rectangle(int x1, int y1, int x2, int y2, int x3, int y3, int x4, int y4);
    void add_circle(int x, int y, int radius);
    int nb_obstacles();
    int nb_vertices(int id_polygon);
    VisiLibity::Point get_obstacle_vertice(int id_polygon, int id_vertice);
    Exception build_environment();
    void reset_environment();
    VisiLibity::Polyline path(int x_start, int y_start, int x_end, int y_end);


private:
    double _epsilon_vis;
    VisiLibity::Environment _environment;
    VisiLibity::Visibility_Graph _visibility_graph;
    Table _table;
};

#endif // POLYGON_H
