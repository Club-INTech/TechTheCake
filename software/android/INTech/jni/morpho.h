#ifndef MORPHO_H
#define MORPHO_H

#include <opencv2/core/core.hpp>

class Morpho
{
public:
    Morpho();
    static void erosion(cv::Mat &src, cv::Mat &dst, int erosion_size);
    static void dilatation(cv::Mat &src, cv::Mat &dst, int dilation_size);
    static void closing(cv::Mat &src, cv::Mat &dst, int closing_size);

private:
    static cv::Mat getKernel(int size);
};

#endif // MORPHO_H
