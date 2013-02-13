#include <jni.h>
#include <opencv2/core/core.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/features2d/features2d.hpp>
#include <vector>

using namespace std;
using namespace cv;

extern "C" {
JNIEXPORT void JNICALL Java_intech_android_DisplayImageActivity_test(JNIEnv*, jobject, jlong addrGray);

JNIEXPORT void JNICALL Java_intech_android_DisplayImageActivity_test(JNIEnv*, jobject, jlong addrGray)
{
    Mat& image  = *(Mat*)addrGray;
    circle(image, Point(0, 0), 10, Scalar(0,0,255), 3);
}
}
