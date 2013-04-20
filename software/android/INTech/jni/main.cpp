#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/opencv.hpp>
#include <iostream>
#include <stdio.h>
#include <vector>

#include "processing.h"
#include "morpho.h"
#include "model.h"

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

/*
void em(Mat source)
{
    // image H seulement
    Mat hsv;
    Mat h_img(source.rows, source.cols, CV_8UC3);
    cvtColor(source, hsv, COLOR_BGR2HSV);

    for (int x = 0; x < hsv.rows; x++) {
        for (int y = 0; y < hsv.cols; y++) {
            h_img.at<Vec3b>(x, y)[0] = hsv.at<Vec3b>(x, y)[0];
            h_img.at<Vec3b>(x, y)[1] = hsv.at<Vec3b>(x, y)[0];
            h_img.at<Vec3b>(x, y)[2] = hsv.at<Vec3b>(x, y)[0];
        }
    }


    //ouput images
    cv::Mat meanImg(source.rows, source.cols, CV_32FC3);
    cv::Mat fgImg(source.rows, source.cols, CV_8UC3);
    cv::Mat bgImg(source.rows, source.cols, CV_8UC3);

    //convert the input image to float
    cv::Mat floatSource;
    h_img.convertTo(floatSource, CV_32F);



    //now convert the float image to column vector
    cv::Mat samples(h_img.rows * h_img.cols, 1, CV_32FC1);
    int idx = 0;
    for (int y = 0; y < h_img.rows; y++) {
        cv::Vec3f* row = floatSource.ptr<cv::Vec3f> (y);
        for (int x = 0; x < h_img.cols; x++) {
            samples.at<cv::Vec3f> (idx++, 0) = row[x];
        }
    }

    cv::EMParams params(10);
    cv::ExpectationMaximization em(samples, cv::Mat(), params);

    //the two dominating colors
    cv::Mat means = em.getMeans();
    //the weights of the two dominant colors
    cv::Mat weights = em.getWeights();

    //we define the foreground as the dominant color with the largest weight
    const int fgId = 0;

    for (int i = 0; i < weights.cols; i++)
    {
        cout << "Poids n°" << i << ": " << weights.at<float>(i) << endl;
    }

    //now classify each of the source pixels
    idx = 0;
    for (int y = 0; y < h_img.rows; y++) {
        for (int x = 0; x < h_img.cols; x++) {

            //classify
            const int result = cvRound(em.predict(samples.row(idx++), NULL));
            //get the according mean (dominant color)
            const double* ps = means.ptr<double>(result, 0);

            //set the according mean value to the mean image
            float* pd = meanImg.ptr<float>(y, x);
            //float images need to be in [0..1] range
            pd[0] = ps[0] / 255.0;
            pd[1] = ps[1] / 255.0;
            pd[2] = ps[2] / 255.0;

//            //set either foreground or background
//            if (result == fgId) {
//                fgImg.at<cv::Point3_<uchar> >(y, x, 0) = source.at<cv::Point3_<uchar> >(y, x, 0);
//            } else {
//                bgImg.at<cv::Point3_<uchar> >(y, x, 0) = source.at<cv::Point3_<uchar> >(y, x, 0);
//            }
        }
    }



    namedWindow("Source", CV_WINDOW_NORMAL);
    namedWindow("H", CV_WINDOW_NORMAL);
    namedWindow("Means", CV_WINDOW_NORMAL);
//    namedWindow("Foreground", CV_WINDOW_NORMAL);
//    namedWindow("Background", CV_WINDOW_NORMAL);

    cv::imshow("Source", source);
    cv::imshow("Means", meanImg);
    cv::imshow("H", h_img);
//    cv::imshow("Foreground", fgImg);
//    cv::imshow("Background", bgImg);
}
*/

int main(int argc, char** argv)
{
    if (argc != 3)
    {
        cout << "2 arguments attendus: <chemin vers l'image> <couleur = (r|b)>" << endl;
        return 1;
    }

    if (argv[2][0] == 'b')
    {
        processing.model = Model::getRepartitionModel('b');
    }

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

