#ifndef BALL_H
#define BALL_H

#include <map>
#include <opencv2/core/core.hpp>

class Ball
{
public:
    enum Type {
        UNVALID_BALL, RED_BALL, BLUE_BALL, WHITE_BALL
    };
    struct CheckPoint {
        cv::Point2f point;
        Type type;
    };
    Ball(cv::Point2f center, float radius, bool detected_firstime = true);
    int getId();
    void setId(int id);
    Type getType();
    void setType(Type type);
    std::vector<CheckPoint> getCheckPoints();
    void setCheckPoints(std::vector<CheckPoint> points);
    bool isFirstTimeDetected();
    cv::Point2f getCenter();
    float getRadius();
    float distanceWith(cv::Point2f &point);
    void distanceWithClosestPoint(std::map<int,cv::Point2f> &model, float &distance, int &id, bool auto_ignore = false);
    void distanceWithClosestBall(std::vector<Ball*> &balls, float &distance);
    static cv::Scalar getColorScalar(Type type);

private:
    int id;
    cv::Point2f center;
    float radius;
    Type type;
    std::vector<CheckPoint> check_points;
    bool detected_firstime;
};

#endif // BALL_H
