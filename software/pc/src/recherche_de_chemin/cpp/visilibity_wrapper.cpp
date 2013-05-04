#include "visilibity_wrapper.h"

#include <iostream>

using namespace std;

VisilibityWrapper::VisilibityWrapper(int width, int height):
    _table(width, height)
{
}

void VisilibityWrapper::epsilon(double e)
{
    _epsilon = e;
}

void VisilibityWrapper::define_map_dimensions(int width, int height)
{
    // Construction du polygone
    vector<VisiLibity::Point> points;
    points.push_back(VisiLibity::Point(0, 0));
    points.push_back(VisiLibity::Point(width, 0));
    points.push_back(VisiLibity::Point(width, height));
    points.push_back(VisiLibity::Point(0, height));
    VisiLibity::Polygon polygon = VisiLibity::Polygon(points);
}

void VisilibityWrapper::add_rectangle(int x1, int y1, int x2, int y2, int x3, int y3, int x4, int y4)
{
    // Création du polygone
    vector<cv::Point> points;
    points.push_back(cv::Point(x1, y1));
    points.push_back(cv::Point(x2, y2));
    points.push_back(cv::Point(x3, y3));
    points.push_back(cv::Point(x4, y4));

    // Ajout du rectangle sur la table
    _table.add_polygon(points);
}

void VisilibityWrapper::add_circle(int x, int y, int radius)
{
    // Transformation du cercle en polygone
    // TODO
}

VisilibityWrapper::Exception VisilibityWrapper::build_environment()
{
    // Récupération des obstacles de la table
    vector<VisiLibity::Polygon> obstacles = _table.get_obstacles();

    // Affichage des résultats
    _table.display();

    // Construction de l'environnement
    _environment = VisiLibity::Environment(obstacles);

    // Vérification de la validité
    if (!_environment.is_valid(_epsilon))
    {
        return VisilibityWrapper::ENVIRONMENT_IS_NOT_VALID;
    }

    // Construction du graphe de visibilité
    _visibility_graph = VisiLibity::Visibility_Graph(_environment, _epsilon);

    return VisilibityWrapper::RETURN_OK;
}

void VisilibityWrapper::reset_environment()
{
    _table.reset();
}

VisiLibity::Polyline VisilibityWrapper::path(int x_start, int y_start, int x_end, int y_end)
{
    VisiLibity::Point start(x_start, y_start);
    VisiLibity::Point end(x_end, y_end);

    return _environment.shortest_path(start, end, _visibility_graph, _epsilon);
}
