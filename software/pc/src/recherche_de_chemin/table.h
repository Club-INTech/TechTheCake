#ifndef TABLE_H
#define TABLE_H

#include <opencv2/imgproc/imgproc.hpp>
#include <vector>

#include "visilibity.hpp"

class Table
{
public:
    Table(int width, int height, int ratio, double tolerance_cv);
    void reset();
    void add_polygon(std::vector<cv::Point> polygon);
    std::vector<VisiLibity::Polygon> get_obstacles();
    void display();

private:
    void print(VisiLibity::Polygon polygon);
    cv::Point to_opencv_coordinates(cv::Point point);
    VisiLibity::Point to_table_coordinates(cv::Point cv);

private:
    int _width, _height;
    int _ratio;
    double _tolerance_cv;
    cv::Mat _image;                    // accumule les obstacles
    cv::Mat _image_xor;                // XOR pour le contour des bords
    cv::Mat _image_bords_contours;     // remplissage du XOR permettant un ET logique
    cv::Mat _image_bords_polygon;      // seulement pour débug
    cv::Mat _image_obstacles;          // ET logique pour retirer les bords
    cv::Mat _image_obstacles_polygons; // seulement pour débug
};

#endif // TABLE_H
