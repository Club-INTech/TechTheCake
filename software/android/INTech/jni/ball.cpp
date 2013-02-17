#include "ball.h"
#include "define.h"

#include <algorithm>
#include <iostream>

using namespace cv;
using namespace std;

Ball::Ball(Point2f center, float radius, bool detected_firstime):
    id(0),
    center(center),
    radius(radius),
    detected_firstime(detected_firstime)
{
    // Point de contrôle par défaut
    Point2f point(center);
    CheckPoint check_point;
    check_point.point = point;
    check_point.type = BLUE_BALL;

    // Liste des points de contrôle
    check_point.point.y += 3 * radius / 2;
    check_points.push_back(check_point);
    check_point.point.x += 3 * radius / 4;
    check_points.push_back(check_point);
    check_point.point.x -= 6 * radius / 4;
    check_points.push_back(check_point);
}

int Ball::getId()
{
    return id;
}

void Ball::setId(int id)
{
    this->id = id;
}

Point2f Ball::getCenter()
{
    return center;
}

float Ball::getRadius()
{
    return radius;
}

Ball::Type Ball::getType()
{
    return type;
}

void Ball::setType(Type t)
{
    type = t;
}

vector<Ball::CheckPoint> Ball::getCheckPoints()
{
    return check_points;
}

void Ball::setCheckPoints(vector<Ball::CheckPoint> points)
{
    check_points = points;

    // Détermine la couleur en fonction de la majorité des check_points
    int results[4] = {0, 0, 0, 0};
    for (vector<CheckPoint>::iterator point = check_points.begin(); point != check_points.end(); ++point)
    {
        results[point->type]++;
    }

    type = (Type) (max_element(results, results + 4) - results);
}

bool Ball::isFirstTimeDetected()
{
    return detected_firstime;
}

float Ball::distanceWith(Point2f &point)
{
    return (point.x - center.x) * (point.x - center.x) + (point.y- center.y) * (point.y - center.y);
}

void Ball::distanceWithClosestPoint(map<int,Point2f> &model, float &distance, int &id, bool auto_ignore)
{
    float min_d = numeric_limits<float>::max();
    int current_id;
    map<int,Point2f>::iterator iterator;

    for (iterator = model.begin(); iterator != model.end(); ++iterator)
    {
        float d = distanceWith(iterator->second);

        if (min_d >= d && (d > 0 || !auto_ignore))
        {
            min_d = d;
            current_id = iterator->first;
        }
    }

    distance = min_d;
    id = current_id;
}

void Ball::distanceWithClosestBall(vector<Ball*> &balls, float &distance)
{
    map<int,Point2f> ball_map;

    for (vector<Ball*>::iterator ball = balls.begin(); ball != balls.end(); ++ball)
    {
        Point2f center = (*ball)->getCenter();
        ball_map.insert(pair<int,Point2f>(0,center));
    }

    int id;
    distanceWithClosestPoint(ball_map, distance, id, true);
}

Scalar Ball::getColorScalar(Type type)
{
    Scalar color(0, 0, 0, 255);

    if (type == RED_BALL)
    {
        color = RED_COLOR;
    }
    else if (type == BLUE_BALL)
    {
        color = BLUE_COLOR;
    }
    else if (type == WHITE_BALL)
    {
        color = Scalar(255, 255, 255, 255);
    }

    return color;
}
