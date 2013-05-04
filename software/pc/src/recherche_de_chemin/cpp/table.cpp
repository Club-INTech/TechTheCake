#include "table.h"

#include <opencv2/imgproc/imgproc.hpp>

#if DISPLAY_DEBUG_WINDOWS
#include <opencv2/highgui/highgui.hpp>
#endif

using namespace std;
using namespace cv;

typedef vector<Point> Contour;
typedef vector<Point> Polygon;

Table::Table(int width, int height):
    _width(width),
    _height(height),
    _image(height, width, CV_8U),
    _image_contours(height, width, CV_8U),
    _image_polygons(height, width, CV_8U)
{
    reset();
}

void Table::reset()
{
    _image = Mat(_height, _width, CV_8U);
}

void Table::tolerance_cv(double t)
{
    _tolerance_cv = t;
}

void Table::add_polygon(vector<Point> polygon)
{
    // Tableau de points (fillPoly ne prend pas de vector)
    Point *points = &polygon[0];
    int ntab = polygon.size();

    // Remplissage du polygone
    fillPoly(_image, (const Point **) &points, &ntab, 1, Scalar(255));
}

vector<VisiLibity::Polygon> Table::get_obstacles()
{
    // Détection des contours
    Mat image_copy = _image.clone();
    vector<Contour> contours;
    findContours(image_copy, contours, CV_RETR_EXTERNAL, CV_CHAIN_APPROX_SIMPLE);

#if DISPLAY_DEBUG_WINDOWS
    // Affichage des contours
    drawContours(_image_contours, contours, -1, Scalar(255));
#endif

    // Liste des polygones, un polygone par contour détecté
    vector<Polygon> polygon_contours(contours.size());

    for (int i = 0; i < contours.size(); i++)
    {
        // Détermine le polygone englobant assez proche
        approxPolyDP(Mat(contours[i]), polygon_contours[i], _tolerance_cv, true);
    }

#if DISPLAY_DEBUG_WINDOWS
    // Affichage des polygones finaux
    drawContours(_image_polygons, polygon_contours, -1, Scalar(255));
#endif

    vector<VisiLibity::Polygon> obstacles;

    // Conversion au format Visilibity
    VisiLibity::Polygon table;
    table.push_back(VisiLibity::Point(0, 0));
    table.push_back(VisiLibity::Point(_width, 0));
    table.push_back(VisiLibity::Point(_width, _height));
    table.push_back(VisiLibity::Point(0, _height));

    // 1er obstacle: contours de la table
    obstacles.push_back(table);

    for (vector<Polygon>::iterator polygon = polygon_contours.begin(); polygon != polygon_contours.end(); polygon++)
    {
        // Construction du polygone, dans l'ordre inverse pour visilibity
        VisiLibity::Polygon visilibity_polygon;

        for (int i = 0; i < polygon->size(); i++)
        {
            Point point = (*polygon)[i];
            visilibity_polygon.push_back(VisiLibity::Point(point.x, point.y));
        }

        obstacles.push_back(visilibity_polygon);
    }

    return obstacles;
}

void Table::display()
{
#if DISPLAY_DEBUG_WINDOWS
    namedWindow("Table", CV_WINDOW_AUTOSIZE);
    namedWindow("Contours", CV_WINDOW_AUTOSIZE);
    namedWindow("Polygons", CV_WINDOW_AUTOSIZE);

    imshow("Table", _image);
    imshow("Contours", _image_contours);
    imshow("Polygons", _image_polygons);
    cvvWaitKey(0);
#endif
}

void Table::print(VisiLibity::Polygon polygon)
{
    cout << polygon << endl;
}

Point Table::to_opencv_coordinates(Point p)
{
    //Changement de repère pour traiter avec opencv
//     int x_cv = (p.x + 
    return p;
}

Point Table::to_table_coordinates(Point p)
{
//     VisiLibity::Point(
        
    return p;
}
