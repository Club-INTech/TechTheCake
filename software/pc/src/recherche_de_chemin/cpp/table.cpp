#include "table.h"

#include <opencv2/imgproc/imgproc.hpp>

#if DISPLAY_DEBUG_WINDOWS
#include <opencv2/highgui/highgui.hpp>
#endif

using namespace std;

typedef vector<cv::Point> Contour;
typedef vector<cv::Point> Polygon;

Table::Table(int width, int height, float ratio):
    _width(width),
    _height(height),
    _ratio(ratio),
    _image(height*ratio, width*ratio, CV_8U),
    _image_contours(height*ratio, width*ratio, CV_8U),
    _image_polygons(height*ratio, width*ratio, CV_8U)
{
    reset();
}

void Table::reset()
{
    _image = cv::Mat(_height*_ratio, _width*_ratio, CV_8U);
}

void Table::tolerance_cv(double t)
{
    _tolerance_cv = t;
}

void Table::add_polygon(vector<cv::Point> polygon)
{
    // Tableau de points (fillPoly ne prend pas de vector)
    cv::Point *points = &polygon[0];
    int ntab = polygon.size();
    
    for (int i=0; i<ntab; i++)
    {
        points[i] = to_opencv_coordinates(points[i]);
    }

    // Remplissage du polygone
    cv::fillPoly(_image, (const cv::Point **) &points, &ntab, 1, cv::Scalar(255));
}

vector<VisiLibity::Polygon> Table::get_obstacles()
{
    // Détection des contours
    cv::Mat image_copy = _image.clone();
    vector<Contour> contours;
    cv::findContours(image_copy, contours, CV_RETR_EXTERNAL, CV_CHAIN_APPROX_SIMPLE);

#if DISPLAY_DEBUG_WINDOWS
    // Affichage des contours
    drawContours(_image_contours, contours, -1, cv::Scalar(255));
#endif

    // Liste des polygones, un polygone par contour détecté
    vector<Polygon> polygon_contours(contours.size());

    for (int i = 0; i < contours.size(); i++)
    {
        // Détermine le polygone englobant assez proche
        cv::approxPolyDP(cv::Mat(contours[i]), polygon_contours[i], _tolerance_cv, true);
    }

#if DISPLAY_DEBUG_WINDOWS
    // Affichage des polygones finaux
    drawContours(_image_polygons, polygon_contours, -1, cv::Scalar(255));
#endif

    vector<VisiLibity::Polygon> obstacles;

    // Conversion au format Visilibity
    VisiLibity::Polygon table;
    table.push_back(VisiLibity::Point(-_width/2, 0));
    table.push_back(VisiLibity::Point(_width/2, 0));
    table.push_back(VisiLibity::Point(_width/2, _height));
    table.push_back(VisiLibity::Point(-_width/2, _height));

    // 1er obstacle: contours de la table
    obstacles.push_back(table);

    for (vector<Polygon>::iterator polygon = polygon_contours.begin(); polygon != polygon_contours.end(); polygon++)
    {
        // Construction du polygone, dans l'ordre inverse pour visilibity
        VisiLibity::Polygon visilibity_polygon;

        for (int i = polygon->size()-1; i >= 0; i--)
        {
            cv::Point point = (*polygon)[i];
            visilibity_polygon.push_back(to_table_coordinates(point));
        }

        obstacles.push_back(visilibity_polygon);
    }

    return obstacles;
}

void Table::display()
{
#if DISPLAY_DEBUG_WINDOWS
    cv::namedWindow("Table", CV_WINDOW_AUTOSIZE);
    cv::namedWindow("Contours", CV_WINDOW_AUTOSIZE);
    cv::namedWindow("Polygons", CV_WINDOW_AUTOSIZE);

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

cv::Point Table::to_opencv_coordinates(cv::Point point)
{
    //Changement de repère pour traiter avec opencv
    int cv_x = (point.x + _width/2) * _ratio;
    int cv_y = - (point.y - _height) * _ratio;
    return cv::Point(cv_x, cv_y);
}

VisiLibity::Point Table::to_table_coordinates(cv::Point cv)
{
    //Changement de repère pour traiter avec visilibity
    int vis_x = (cv.x / _ratio) - _width/2;
    int vis_y = - (cv.y / _ratio) + _height;
    return VisiLibity::Point(vis_x, vis_y);
}
