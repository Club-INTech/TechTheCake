#ifndef MODEL_H
#define MODEL_H

#include <string>
#include <map>

#include <opencv2/core/core.hpp>

class Model
{
public:
    static std::map<int,cv::Point2f> getRepartitionModel(char color);
};

#endif // MODEL_H
