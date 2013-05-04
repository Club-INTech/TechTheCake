#ifndef TABLE_H
#define TABLE_H

#include <opencv2/imgproc/imgproc.hpp>
#include <vector>

#include "visilibity.hpp"

class Table
{
public:
    Table(int width, int height, float ratio);
    void reset();
    void tolerance_cv(double t);
    void add_polygon(std::vector<cv::Point> polygon);
    std::vector<VisiLibity::Polygon> get_obstacles();
    void display();

private:
    void print(VisiLibity::Polygon polygon);
    cv::Point to_opencv_coordinates(cv::Point point);
    VisiLibity::Point to_table_coordinates(cv::Point cv);

private:
    int _width, _height;
    float _ratio;
    double _tolerance_cv;
    cv::Mat _image;
    cv::Mat _image_contours;
    cv::Mat _image_polygons;
};

#endif // TABLE_H
