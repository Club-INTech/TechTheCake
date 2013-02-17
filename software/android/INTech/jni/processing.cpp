#include "processing.h"
#include "morpho.h"
#include "ballidentifier.h"
#include "model.h"
#include "define.h"

#include <sstream>
#include <iostream>
#include <string>
#include <vector>
#include <map>

#include <opencv2/imgproc/imgproc.hpp>

using namespace cv;
using namespace std;

Processing::Processing():
    cake_borders(0, 0, 230, 100),
    model(Model::getRepartitionModel("red")),
    image_partition(40),
    erode_kernel_size(0),
    closing_kernel_size(0),
    min_ball_area(90),
    max_ball_area(280),
    min_yellow_color(30, 80, 140),
    max_yellow_color(38, 250, 250),
    blue_ball_color(105),
    red_ball_color(3),
    ball_color_tolerance(10),
    white_ball_tolerance(70)
{
}

Processing::~Processing()
{
    clearResults();
}

Processing& Processing::instance()
{
    static Processing _instance;
    return _instance;
}

void Processing::loadImage(cv::Mat &image)
{
    // Image initiale en BGR
    image_bgr = image;
    image_results = image_bgr.clone();

    // Réduction du bruit
    GaussianBlur(image_bgr, image_bgr, Size(3, 3), 1, 1);

    // Image HSV
#ifdef COMPILE_FOR_ANDROID
    cvtColor(image_bgr, image_hsv, CV_RGB2HSV);
#else
    cvtColor(image_bgr, image_hsv, CV_BGR2HSV);
#endif

    // Extraction de la couleur jaune
    inRange(image_hsv, min_yellow_color, max_yellow_color, raw_balls_mask);
}

void Processing::process()
{
    // Nettoyage des masques
    _cleanBallsMask();

    // Détection des contours sur les balles
    vector<Contour> balls_contours = _findContours(filtered_balls_mask);

    // Affichage des contours sur l'image
    image_contours = image_bgr.clone();
    drawContours(image_contours, balls_contours, -1, Scalar(255, 255, 255, 255));

    // Détection des contours pouvant représenter des balles de tennis
    results = _findBalls(balls_contours);
    cout << results.size() << " forme(s) ressemblant à des balles" << endl;
    if (results.size() == 0) return;

    // Filtre les balles et garde uniquement celles associées à une couleur
    vector<Ball*> balls_with_color = _keepBallsWithColor(results);
    cout << balls_with_color.size() << " balle(s) avec une couleur" << endl;

    // Détecte le centre des balles
    Point2f cake_center = _getApproximativeCakeCenter(balls_with_color);
    cake_borders.x = cake_center.x - cake_borders.width / 2;
    cake_borders.y = cake_center.y - cake_borders.height / 2;

    // Exclusion des balles hors de la zone estimée du gateau
    vector<Ball*> valid_balls = _keepBallsInCakeBorders(balls_with_color);
    cout << valid_balls.size() << " balle(s) dans la zone estimée du gateau" << endl;

    // Identifie les balles selon le modèle
    BallIdentifier detector(model, valid_balls);
    vector<Ball*> new_balls = detector.identifyBalls();

    // De nouvelles balles ont été créée à partir du modèle
    if (new_balls.size() > 0)
    {
        cout << new_balls.size() << " nouvelle(s) balle(s) rattrapée(s)" << endl;

        // Traitement des nouvelles balles créés par le modèle
        for (vector<Ball*>::iterator ball = new_balls.begin(); ball != new_balls.end(); ++ball)
        {
            _findBallColor(image_hsv, *ball);
        }

        results.insert(results.end(), new_balls.begin(), new_balls.end());
    }

    // Affichage des balles sur l'image de résultats
    image_results = image_bgr.clone();
    _drawBalls(results, image_results);

    // Affichage du résultat sur la console
    cout << getResults() << endl;
    cout << "-------------------------------" << endl;
}

string Processing::getResults()
{
    string string_result = "??????????";

    for (vector<Ball*>::iterator result = results.begin(); result != results.end(); ++result)
    {
        Ball *ball = *result;

        if (ball->getType() != Ball::UNVALID_BALL && ball->getId() > 0)
        {
            char letter;

            switch (ball->getType())
            {
            case Ball::RED_BALL:
                letter = 'r';
                break;
            case Ball::BLUE_BALL:
                letter = 'b';
                break;
            case Ball::WHITE_BALL:
                letter = 'w';
                break;
            default:
                break;
            }

            string_result[ball->getId()-1] = letter;
        }
    }

    return string_result;
}

void Processing::clearResults()
{
    for (vector<Ball*>::iterator ball = results.begin(); ball != results.end(); ++ball)
    {
        if (*ball != 0)
        {
            delete *ball;
        }
    }
}

void Processing::_cleanBallsMask()
{
    Morpho::closing(raw_balls_mask, filtered_balls_mask, closing_kernel_size);
    Morpho::erosion(filtered_balls_mask, filtered_balls_mask, erode_kernel_size);
}

vector<Processing::Contour> Processing::_findContours(Mat &mask)
{
    // Détection des contours sur l'image (binaire)
    vector<Processing::Contour> contours;
    Mat clone_mask = mask.clone();
    findContours(clone_mask, contours, CV_RETR_EXTERNAL, CV_CHAIN_APPROX_SIMPLE);

    // Garde l'enveloppe convexe des contours détectés
    vector<Processing::Contour> convex_contours;
    for (vector<Processing::Contour>::iterator contour = contours.begin(); contour != contours.end(); ++contour)
    {
        Processing::Contour convex_contour;
        convexHull(*contour, convex_contour);
        convex_contours.push_back(convex_contour);
    }

    return convex_contours;
}

Processing::Contour Processing::_getBiggestContour(vector<Contour> &contours)
{
    double max_area = 0;
    Contour max_contour;

    for (vector<Contour>::iterator contour = contours.begin(); contour != contours.end(); ++contour)
    {
        double area = contourArea(*contour);

        if (area > max_area)
        {
            max_area = area;
            max_contour = *contour;
        }
    }

    return max_contour;
}

vector<Ball*> Processing::_findBalls(vector<Contour> &contours)
{
    // Filtre les contours qui ne rentrent pas dans l'intervalle de taille admissible
    vector<Ball*> balls;
    double average_area = 0;

    for (vector<Contour>::iterator contour = contours.begin(); contour != contours.end(); ++contour)
    {
        // Vérification de la surface du contour
        double area = contourArea(*contour);
        if (area < min_ball_area || area > max_ball_area)
        {
            continue;
        }

        // Détection du cercle englobant
        Point2f center;
        float radius;
        minEnclosingCircle(*contour, center, radius);

        // Vérifie que le cercle est dans la zone à analyser
        if (center.y > image_bgr.rows * image_partition / 100)
        {
            continue;
        }

        // Création de la balle
        Ball *ball = new Ball(center, radius);

        // Vérification de la couleur
        _findBallColor(image_hsv, ball);

        balls.push_back(ball);
        average_area += area;
    }

    if (balls.size() > 0) average_area /= balls.size();
    std::cout << "Surface moyenne des balles: " << average_area << std::endl;

    return balls;
}


void Processing::_findBallColor(Mat &image, Ball *ball)
{
    vector<Ball::CheckPoint> check_points = ball->getCheckPoints();
    vector<Ball::CheckPoint> check_points_analyzed;

    // Détermine la couleur de chaque point de contrôle
    for (vector<Ball::CheckPoint>::iterator point = check_points.begin(); point != check_points.end(); ++point)
    {
        Vec3b color = image.at<Vec3b>(point->point);
        point->type = _analyzeColor(color);
        check_points_analyzed.push_back(*point);
    }

    // Mise à jour des checkPoints, détermine la couleur de la balle
    ball->setCheckPoints(check_points_analyzed);
}

vector<Ball*> Processing::_keepBallsWithColor(vector<Ball*> &balls)
{
    vector<Ball*> valid_balls;

    for (vector<Ball*>::iterator iterator = balls.begin(); iterator != balls.end(); ++iterator)
    {
        Ball *ball = *iterator;

        // Aucune détection de couleur
        if (ball->getType() == Ball::UNVALID_BALL)
        {
            continue;
        }

        valid_balls.push_back(ball);
    }

    return valid_balls;
}

vector<Ball*> Processing::_keepBallsInCakeBorders(vector<Ball*> &balls)
{
    vector<Ball*> valid_balls;

    for (vector<Ball*>::iterator iterator = balls.begin(); iterator != balls.end(); ++iterator)
    {
        Ball *ball = *iterator;

        if (cake_borders.contains(ball->getCenter()))
        {
            valid_balls.push_back(ball);
        }
    }

    return valid_balls;
}

Point2f Processing::_getApproximativeCakeCenter(vector<Ball*> &balls)
{
    vector<int> x;
    vector<int> y;

    for (vector<Ball*>::iterator ball = balls.begin(); ball != balls.end(); ++ball)
    {
        x.push_back((*ball)->getCenter().x);
        y.push_back((*ball)->getCenter().y);
    }

    sort(x.begin(), x.end());
    sort(y.begin(), y.end());
    unsigned int med = balls.size() / 2;

    if (balls.size() == 0) return Point2f(0, 0);

    return Point2f(x.at(med), y.at(med));
}

Ball::Type Processing::_analyzeColor(Vec3b color)
{
    int h = (int) color[0];
    int s = (int) color[1];
    int v = (int) color[2];

    if (s <= white_ball_tolerance && v >= 255 - white_ball_tolerance)
    {
        return Ball::WHITE_BALL;
    }

    if (h >= blue_ball_color - ball_color_tolerance && h <= blue_ball_color + ball_color_tolerance)
    {
        return Ball::BLUE_BALL;
    }

    if (h >= red_ball_color - ball_color_tolerance && h <= red_ball_color + ball_color_tolerance)
    {
        return Ball::RED_BALL;
    }

    return Ball::UNVALID_BALL;
}

void Processing::_drawBalls(vector<Ball*> &balls, Mat &image)
{
    // Affichage de la zone du gateau estimée
    rectangle(image, cake_borders, Scalar(0, 0, 0, 255));

    // Affichage des balles
    for (vector<Ball*>::iterator ball_iterator = balls.begin(); ball_iterator != balls.end(); ++ball_iterator)
    {
        Ball *ball = *ball_iterator;

        // Cercle entourant la balle
        circle(image, ball->getCenter(), ball->getRadius(), Ball::getColorScalar(ball->getType()), 1);

        // Id de la balle
        int id = ball->getId();
        if (id > 0)
        {
            stringstream stream;
            stream << id;
            string id_string = stream.str();

            // Couleur noire si rattrapée par le modèle
            Scalar color = (ball->isFirstTimeDetected()) ? Ball::getColorScalar(ball->getType()) : Scalar(0, 0, 0, 255);

            Point2f position(ball->getCenter().x - ball->getRadius() / 2, ball->getCenter().y + ball->getRadius() / 2);
            putText(image, id_string, position, FONT_HERSHEY_PLAIN, 0.8, color);
        }

        // Liste des points servant à la détection de la couleur
        std::vector<Ball::CheckPoint> check_points = ball->getCheckPoints();
        std::vector<Ball::CheckPoint>::iterator iterator;
        for (iterator = check_points.begin(); iterator != check_points.end(); ++iterator)
        {
            Point p(iterator->point.x, iterator->point.y);
            line(image, p, p, Ball::getColorScalar(iterator->type), 2);
        }
    }
}

