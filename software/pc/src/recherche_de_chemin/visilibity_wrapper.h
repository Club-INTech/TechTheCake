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
    VisilibityWrapper(int width, int height, int ratio, double tolerance_cv, double epsilon_vis, int rayon_tolerance);
    void add_rectangle(int x1, int y1, int x2, int y2, int x3, int y3, int x4, int y4);
    void add_circle(int x, int y, int radius);
    int nb_obstacles();
    VisiLibity::Polygon get_obstacle(int id_polygon);
    Exception build_environment();
    void reset_environment();
    VisiLibity::Polyline path(int x_start, int y_start, int x_end, int y_end);


private:
    double _epsilon_vis;
    int _rayon_tolerance;
    VisiLibity::Environment _environment;
    VisiLibity::Visibility_Graph _visibility_graph;
    Table _table;
};

#endif // POLYGON_H
