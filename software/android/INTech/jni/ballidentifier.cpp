#include "ballidentifier.h"

#include <iostream>

using namespace std;
using namespace cv;

BallIdentifier::BallIdentifier(map<int,Point2f> &model, vector<Ball*> &balls):
    model(model),
    balls(balls)
{

}

vector<Ball*> BallIdentifier::identifyBalls(float &model_distance)
{
    vector<Ball*> new_balls;

    if (balls.size() == 0) return new_balls;

    // Récupère le modèle le plus proche
    map<int,Point2f> closest_model = _findClosestModel(model_distance);

    // Identifie les balles
    _identifyBallsWithModel(closest_model, balls);

    // Au cas où toutes les balles ne sont pas identifiées, tentative de reconstitution
    if (_getIdsDetected(balls).size() > 1 && _getIdsDetected(balls).size() < 10)
    {
        new_balls = _createRemainingBall(closest_model, balls);
    }

    return new_balls;
}

map<int,Point2f> BallIdentifier::_findClosestModel(float &model_distance)
{
    // Balle servant de référence pour la translation
    Ball reference = *balls.at(0);
    Point2f reference_center = reference.getCenter();

    // Modèle ayant le plus de correspondances
    map<int,Point2f> closest_model;

    float min_error = numeric_limits<float>::max();
    map<int,Point2f>::iterator model_iterator;

    // Tentatives de translation du modèle pour coller à la disposation actuelle des balles
    for (model_iterator = model.begin(); model_iterator != model.end(); ++model_iterator)
    {
        Point2f translation(reference_center.x - model_iterator->second.x, reference_center.y - model_iterator->second.y);
        map<int,Point2f> translated_model;

        for (map<int,Point2f>::iterator iterator = model.begin(); iterator != model.end(); ++iterator)
        {
            Point2f original_point = iterator->second;
            Point2f translated_point(original_point.x + translation.x, original_point.y + translation.y);
            translated_model.insert(pair<int,Point2f>(iterator->first,translated_point));
        }

        float error = _errorWithModel(translated_model, balls);

        if (error < min_error)
        {
            min_error = error;
            closest_model = translated_model;
        }
    }

    cout << "Distance au modèle: " << min_error << endl;
    model_distance = min_error;

    return closest_model;
}


float BallIdentifier::_errorWithModel(map<int,Point2f> &model, vector<Ball*> &balls)
{
    float sum_error = 0;

    for (vector<Ball*>::iterator iterator = balls.begin(); iterator != balls.end(); ++iterator)
    {
        Ball *ball = *iterator;
        float error = 0;
        int id = 0;
        ball->distanceWithClosestPoint(model, error, id);
        sum_error += error;
    }

    return sum_error;
}

void BallIdentifier::_identifyBallsWithModel(map<int,Point2f> &model, vector<Ball*> &balls)
{
    for (vector<Ball*>::iterator iterator = balls.begin(); iterator != balls.end(); ++iterator)
    {
        Ball *ball = *iterator;
        float error = 0;
        int id = 0;
        ball->distanceWithClosestPoint(model, error, id);
        ball->setId(id);
    }
}

vector<int> BallIdentifier::_getIdsDetected(vector<Ball*> &balls)
{
    vector<int> ids;

    for (vector<Ball*>::iterator iterator = balls.begin(); iterator != balls.end(); ++iterator)
    {
        Ball *ball = *iterator;
        if (ball->getId() > 0)
        {
            ids.push_back(ball->getId());
        }
    }

    return ids;
}

vector<Ball*> BallIdentifier::_createRemainingBall(map<int,Point2f> &model, vector<Ball*> &balls)
{
    vector<int> ids_detected = _getIdsDetected(balls);
    vector<Ball*> new_balls;

    for (map<int,Point2f>::iterator model_ball = model.begin(); model_ball != model.end(); ++model_ball)
    {
        int id = model_ball->first;

        // Balle non détectée
        if (find(ids_detected.begin(), ids_detected.end(), id) == ids_detected.end())
        {
            Ball *ball = new Ball(model_ball->second, 10, false);
            ball->setId(id);
            new_balls.push_back(ball);
        }
    }

    return new_balls;
}

