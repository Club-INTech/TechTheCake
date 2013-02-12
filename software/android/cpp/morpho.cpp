#include "morpho.h"

#include <opencv2/imgproc/imgproc.hpp>

using namespace cv;

Morpho::Morpho()
{
}

void Morpho::erosion(Mat &src, Mat &dst, int erosion_size)
{
    Mat kernel = getKernel(erosion_size);
    erode(src, dst, kernel);
}

void Morpho::dilatation(Mat &src, Mat &dst, int dilation_size)
{
    Mat kernel = getKernel(dilation_size);
    dilate(src, dst, kernel);
}

void Morpho::closing(Mat &src, Mat &dst, int closing_size)
{
    Mat kernel = getKernel(closing_size);
    morphologyEx(src, dst, MORPH_CLOSE, kernel);
}

Mat Morpho::getKernel(int size)
{
    return getStructuringElement(MORPH_ELLIPSE, Size(2*size + 1, 2*size + 1), Point(size, size));
}
