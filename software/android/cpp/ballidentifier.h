#ifndef BALLDETECTOR_H
#define BALLDETECTOR_H

#include "ball.h"
#include <vector>
#include <map>

class BallIdentifier
{
public:
    BallIdentifier(std::map<int,cv::Point2f> &model, std::vector<Ball*> &balls);
    std::vector<Ball*> identifyBalls();

private:
    float _errorWithModel(std::map<int,cv::Point2f> &model, std::vector<Ball*> &balls);
    void _identifyBallsWithModel(std::map<int,cv::Point2f> &model, std::vector<Ball*> &balls);
    std::vector<Ball*> _createRemainingBall(std::map<int,cv::Point2f> &model, std::vector<Ball*> &balls);
    std::map<int,cv::Point2f> _findClosestModel();
    std::vector<int> _getIdsDetected(std::vector<Ball*> &balls);

private:
    std::map<int,cv::Point2f> &model;
    std::vector<Ball*> &balls;
    Ball *left_ball;
    Ball *right_ball;
};

#endif // BALLDETECTOR_H
