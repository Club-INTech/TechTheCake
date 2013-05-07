#include "table.h"

#include <opencv2/imgproc/imgproc.hpp>

#if DISPLAY_DEBUG_WINDOWS
#include <opencv2/highgui/highgui.hpp>
#endif

using namespace std;

typedef vector<cv::Point> Contour;
typedef vector<cv::Point> Polygon;

Table::Table(int width, int height, int ratio, double tolerance_cv):
    _width(width),
    _height(height),
    _ratio(ratio),
    _tolerance_cv(tolerance_cv),
    _image(height/ratio, width/ratio, CV_8U),
    _image_xor(height/ratio, width/ratio, CV_8U),
    _image_bords_contours(height/ratio, width/ratio, CV_8U),
    _image_bords_polygon(height/ratio, width/ratio, CV_8U),
    _image_obstacles(height/ratio, width/ratio, CV_8U),
    _image_obstacles_polygons(height/ratio, width/ratio, CV_8U)
{
}

void Table::reset()
{
    _image = cv::Mat::zeros(_height/_ratio, _width/_ratio, CV_8U);
//     _image_xor = cv::Mat::zeros(_height/_ratio, _width/_ratio, CV_8U);
    _image_bords_contours = cv::Mat::zeros(_height/_ratio, _width/_ratio, CV_8U);
#if DISPLAY_DEBUG_WINDOWS
    _image_bords_polygon = cv::Mat::zeros(_height/_ratio, _width/_ratio, CV_8U);
#endif
//     _image_obstacles = cv::Mat::zeros(_height/_ratio, _width/_ratio, CV_8U);
#if DISPLAY_DEBUG_WINDOWS
    _image_obstacles_polygons = cv::Mat::zeros(_height/_ratio, _width/_ratio, CV_8U);
#endif
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
    
    /** recherche des bords de la carte **/
    
    // XOR de l'image de la table
    cv::bitwise_xor(_image, cv::Scalar(255), _image_xor);
    
    // Détection des contours du XOR
    vector<Contour> contours_xor;
#if DISPLAY_DEBUG_WINDOWS
    cv::Mat image_copy = _image_xor.clone(); // Et _image_xor garde la pose pour la photo...
    cv::findContours(image_copy, contours_xor, CV_RETR_EXTERNAL, CV_CHAIN_APPROX_SIMPLE);
#else
    cv::findContours(_image_xor, contours_xor, CV_RETR_EXTERNAL, CV_CHAIN_APPROX_SIMPLE);
#endif
    
    // Approximation polygonale des bords de la carte
    double longueur_max = 0;
    int i_max = 0;
    for (int i = 0; i < contours_xor.size(); i++)
    {
        double longueur = cv::arcLength(contours_xor[i], true);
        if(longueur > longueur_max)
        {
            i_max = i;
            longueur_max = longueur;
        }
    }
    vector<Polygon> bords_contours(1);
    // Détermine le polygone englobant assez proche
    cv::approxPolyDP(cv::Mat(contours_xor[i_max]), bords_contours[0], _tolerance_cv, true);
    
#if DISPLAY_DEBUG_WINDOWS
    // Affichage du polygone final pour les bords
    drawContours(_image_bords_polygon, bords_contours, -1, cv::Scalar(255));
#endif
    
    /** recherche des obstacles intérieurs **/
    
    // Remplissage des contours du XOR
    drawContours(_image_bords_contours, contours_xor, -1, cv::Scalar(255), -1);
    
    // Suppression des bords par ET logique
    cv::bitwise_and(_image, _image_bords_contours, _image_obstacles);
    
    // Détection des contours des obstacles
    vector<Contour> contours_obstacles;
#if DISPLAY_DEBUG_WINDOWS
    image_copy = _image_obstacles.clone();
    cv::findContours(image_copy, contours_obstacles, CV_RETR_EXTERNAL, CV_CHAIN_APPROX_SIMPLE);
#else
    cv::findContours(_image_obstacles, contours_obstacles, CV_RETR_EXTERNAL, CV_CHAIN_APPROX_SIMPLE);
#endif
    
    // Liste des polygones, un polygone par contour détecté
    vector<Polygon> polygones_obstacles(contours_obstacles.size());
    for (int i = 0; i < contours_obstacles.size(); i++)
    {
        // Détermine le polygone englobant assez proche
        cv::approxPolyDP(cv::Mat(contours_obstacles[i]), polygones_obstacles[i], _tolerance_cv, true);
    }

#if DISPLAY_DEBUG_WINDOWS
    // Affichage des polygones finaux pour les obstacles
    drawContours(_image_obstacles_polygons, polygones_obstacles, -1, cv::Scalar(255));
#endif
    
    
    /** conversion en polygones Visilibity 
     
     polygones d'openCV : sens horaire
     polygone des bords de visibility : sens anti-horaire
     polygones des obstacles de visibility : sens horaire
     
    **/
    
    //liste des polygones (sera renvoyée)
    vector<VisiLibity::Polygon> obstacles;
    
    // Polygone des bords de la table (sens anti-horaire)
    VisiLibity::Polygon bords;
    //dans le sens anti-horaire : to_table_coordinates() inverse le sens de définition
    for (int i = 0; i<bords_contours[0].size(); i++)
    {
        cv::Point point = bords_contours[0][i];
        bords.push_back(to_table_coordinates(point));
    }
    obstacles.push_back(bords);

    
    // Polygones des obstacles (sens horaire)
    for (vector<Polygon>::iterator polygon = polygones_obstacles.begin(); polygon != polygones_obstacles.end(); polygon++)
    {
        VisiLibity::Polygon visilibity_polygon;

        // Le sens de définition des polygones est inversé par la transformation to_table_coordinates() : il faut reverser l'ordre des points
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
    cv::namedWindow("XOR", CV_WINDOW_AUTOSIZE);
    cv::namedWindow("Bords contours", CV_WINDOW_AUTOSIZE);
    cv::namedWindow("Bords polygons", CV_WINDOW_AUTOSIZE);
    cv::namedWindow("holes", CV_WINDOW_AUTOSIZE);
    cv::namedWindow("holes polygons", CV_WINDOW_AUTOSIZE);

    imshow("Table", _image);
    imshow("XOR", _image_xor);
    imshow("Bords contours", _image_bords_contours);
    imshow("Bords polygons", _image_bords_polygon);
    imshow("holes", _image_obstacles);
    imshow("holes polygons", _image_obstacles_polygons);
    
    cvvWaitKey(0);
#endif
}

void Table::print(VisiLibity::Polygon polygon)
{
    cout << polygon << endl;
}

cv::Point Table::to_opencv_coordinates(cv::Point point_table)
{
    //Changement de repère pour traiter avec opencv
    int cv_x = (point_table.x + _width/2) / _ratio;
    int cv_y = - (point_table.y - _height) /  _ratio;
    return cv::Point(cv_x, cv_y);
}


VisiLibity::Point Table::to_table_coordinates(cv::Point point_image)
{
    /*
    Changement de repère pour traiter avec visilibity
    avec vérification de l'étanchéité des obstacles qui touchent les bords
    */
    
    float vis_x = (point_image.x * _ratio) - _width/2;
    float vis_y = - (point_image.y * _ratio) + _height;
    
    return VisiLibity::Point(vis_x, vis_y);
}
