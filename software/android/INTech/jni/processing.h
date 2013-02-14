#ifndef PROCESSING_H
#define PROCESSING_H

#include "ball.h"
#include <vector>
#include <opencv2/core/core.hpp>

class Processing
{
public:
    typedef std::vector<cv::Point> Contour;
    static Processing& instance();
    ~Processing();
    void loadImage(cv::Mat &image);
    void process();
    std::string getResults();
    void clearResults();

private:
    Processing();
    void _cleanBallsMask();
    std::vector<Contour> _findContours(cv::Mat &mask);
    Contour _getBiggestContour(std::vector<Contour> &contours);
    void _findBallColor(cv::Mat &image, Ball *ball);
    std::vector<Ball*> _findBalls(std::vector<Processing::Contour> &contours);
    std::vector<Ball*> _keepBallsWithColor(std::vector<Ball*> &balls);
    std::vector<Ball*> _keepBallsInCakeBorders(std::vector<Ball*> &balls);
    cv::Point2f _getApproximativeCakeCenter(std::vector<Ball*> &balls);
    void _drawBalls(std::vector<Ball*> &balls, cv::Mat &image);

public:
    /**
     * @brief Image initiale en BGR
     */
    cv::Mat image_bgr;

    /**
     * @brief Image initiale en HSV
     */
    cv::Mat image_hsv;

    /**
     * @brief Image affichant les résultats
     */
    cv::Mat image_results;

    /**
     * @brief Image affichant les contours détectés
     */
    cv::Mat image_contours;

    /**
     * @brief Masque de couleur sans traitement des balles
     */
    cv::Mat raw_balls_mask;

    /**
     * @brief Masque des balles après traitement
     */
    cv::Mat filtered_balls_mask;

    /**
     * @brief Bordures estimées du gateau
     */
    cv::Rect cake_borders;

    /**
     * @brief Modèle de répartition des balles
     */
    std::map<int,cv::Point2f> model;

    /**
     * @brief Pourcentage de l'image à analyser (à partir du haut), ignore le reste
     */
    int image_partition;

    /**
     * @brief Taille du noyau utilisé pour l'érosion
     */
    int erode_kernel_size;

    /**
     * @brief Taille du noyau utilisé pour la fermeture
     */
    int closing_kernel_size;

    /**
     * @brief Surface minimale d'une balle de tennis
     */
    int min_ball_area;

    /**
     * @brief Surface maximale d'une balle de tennis
     */
    int max_ball_area;

    /**
     * @brief Couleur limite inférieure du jaune des balles
     */
    cv::Scalar min_yellow_color;

    /**
     * @brief Couleur limite supérieure du jaune des balles
     */
    cv::Scalar max_yellow_color;

    /**
     * @brief Tableau contenant les résultats de l'analyse
     */
    std::vector<Ball*> results;
};

#endif // PROCESSING_H
