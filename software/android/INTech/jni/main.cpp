#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <iostream>
#include <stdio.h>
#include <vector>

#include "processing.h"
#include "morpho.h"

using namespace std;
using namespace cv;

Processing processing = Processing::instance();

void updateWindows()
{
    imshow("Mask", processing.filtered_balls_mask);
    imshow("Contours", processing.image_contours);
    imshow("Original", processing.image_results);
}

void maskTrackbarCallback(int, void*)
{
    processing.clearResults();
    processing.process();
    updateWindows();
}

int main(int, char** argv)
{
    Mat src = imread(argv[1], 1);
    processing.loadImage(src);

    namedWindow("Original", CV_WINDOW_NORMAL);
    namedWindow("Contours", CV_WINDOW_NORMAL);
    namedWindow("Mask", CV_WINDOW_NORMAL);
    
    // Erosion
    createTrackbar("Erosion", "Mask", &processing.erode_kernel_size, 20, maskTrackbarCallback);
    
    // Fermeture (dilatation + erosion)
    createTrackbar("Closing", "Mask", &processing.closing_kernel_size, 20, maskTrackbarCallback);

    // Surface min des balles
    createTrackbar("Surface min", "Mask", &processing.min_ball_area, 1000, maskTrackbarCallback);

    // Surface max des balles
    createTrackbar("Surface max", "Mask", &processing.max_ball_area, 2000, maskTrackbarCallback);

    processing.process();
    updateWindows();

    waitKey(0);
    return 0;
}

