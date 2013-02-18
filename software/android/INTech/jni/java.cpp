#include <jni.h>
#include <sstream>
#include <string>
#include <android/log.h>
#include <opencv2/imgproc/imgproc.hpp>
#include "processing.h"

#define LOGI(...) ((void)__android_log_print(ANDROID_LOG_INFO, "INTech-C++", __VA_ARGS__))

extern "C" {

JNIEXPORT void JNICALL Java_intech_android_DisplayImageActivity_loadParameters(
		JNIEnv*, jobject, jint hMin, jint sMin, jint vMin, jint hMax, jint sMax,
		jint vMax);

JNIEXPORT void JNICALL Java_intech_android_DisplayImageActivity_analyze(JNIEnv*,
		jobject, jlong srcAddr, jlong maskAddr, jlong contoursAddr,
		jlong resultsAddr);

JNIEXPORT void JNICALL Java_intech_android_DisplayImageActivity_loadMaskParameters(
		JNIEnv*, jobject, jint maskErode, jint maskClosing);

JNIEXPORT void JNICALL Java_intech_android_DisplayImageActivity_loadBallColorsParameters(
		JNIEnv*, jobject, jint red, jint blue, jint white, jint tolerance);

JNIEXPORT void JNICALL Java_intech_android_DisplayImageActivity_loadBallSizeParameters(
		JNIEnv*, jobject, jint min, jint max);

JNIEXPORT jstring JNICALL Java_intech_android_DisplayImageActivity_getResults(
		JNIEnv*, jobject);

Processing processing = Processing::instance();

JNIEXPORT void JNICALL Java_intech_android_DisplayImageActivity_loadBallsParameters(
		JNIEnv*, jobject, jint hMin, jint sMin, jint vMin, jint hMax, jint sMax,
		jint vMax) {
	processing.min_yellow_color = cv::Scalar(hMin, sMin, vMin);
	processing.max_yellow_color = cv::Scalar(hMax, sMax, vMax);
}

JNIEXPORT void JNICALL Java_intech_android_DisplayImageActivity_loadMaskParameters(
		JNIEnv*, jobject, jint maskErode, jint maskClosing) {
	processing.erode_kernel_size = maskErode;
	processing.closing_kernel_size = maskClosing;
}

JNIEXPORT void JNICALL Java_intech_android_DisplayImageActivity_loadBallSizeParameters(
		JNIEnv*, jobject, jint min, jint max) {
	processing.min_ball_area = min;
	processing.max_ball_area = max;
}

JNIEXPORT void JNICALL Java_intech_android_DisplayImageActivity_loadBallColorsParameters(
		JNIEnv*, jobject, jint red, jint blue, jint tolerance, jint white)
{
	processing.red_ball_color = red;
	processing.blue_ball_color = blue;
	processing.ball_color_tolerance = tolerance;
	processing.white_ball_tolerance = white;
}

JNIEXPORT void JNICALL Java_intech_android_DisplayImageActivity_analyze(JNIEnv*,
		jobject, jlong srcAddr, jlong maskAddr, jlong contoursAddr,
		jlong resultsAddr) {
	cv::Mat &image = *(cv::Mat*) srcAddr;
	cv::Mat &mask = *(cv::Mat*) maskAddr;
	cv::Mat &contours = *(cv::Mat*) contoursAddr;
	cv::Mat &results = *(cv::Mat*) resultsAddr;

	processing.loadImage(image);
	processing.clearResults();
	processing.process();

	mask = processing.filtered_balls_mask;
	contours = processing.image_contours;
	results = processing.image_results;
}

JNIEXPORT jstring JNICALL Java_intech_android_DisplayImageActivity_getResults(JNIEnv* env, jobject) {
	return env->NewStringUTF(processing.getResults().c_str());
}

}

