#include <jni.h>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>

#include "processing.h"

extern "C" {

JNIEXPORT void JNICALL Java_intech_android_DisplayImageActivity_analyze(JNIEnv*,
		jobject, jlong srcAddr, jlong maskAddr, jlong contoursAddr, jlong resultsAddr);

JNIEXPORT void JNICALL Java_intech_android_DisplayImageActivity_analyze(JNIEnv*,
		jobject, jlong srcAddr, jlong maskAddr, jlong contoursAddr, jlong resultsAddr) {
	cv::Mat &image = *(cv::Mat*) srcAddr;
	cv::Mat &mask = *(cv::Mat*) maskAddr;
	cv::Mat &contours = *(cv::Mat*) contoursAddr;
	cv::Mat &results = *(cv::Mat*) resultsAddr;

	Processing processing = Processing::instance();
	processing.loadImage(image);

	processing.process();

	mask = processing.filtered_balls_mask;
	contours = processing.image_contours;
	results = processing.image_results;
}

}

