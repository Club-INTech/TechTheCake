#include "visilibity_wrapper.h"

#include <iostream>
#include <cmath>
#define PI 3.14159265359

using namespace std;

VisilibityWrapper::VisilibityWrapper(int width, int height, int ratio, double tolerance_cv, double epsilon_vis, int rayon_tolerance):
    _table(width, height, ratio, tolerance_cv),
    _epsilon_vis(epsilon_vis),
    _rayon_tolerance(rayon_tolerance)
{
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
    
    int cote_polygone = 50; //longueur minimale d'une arête
    int nbSegments = max(4.,ceil(2*PI*radius/cote_polygone));
    
    // Création du polygone
    vector<cv::Point> points;
    
    for (int i=0;i<nbSegments;i++)
    {
        float theta = -2*i*PI/nbSegments;
        int rayonExinscrit = radius*sqrt(1+sin(PI/(2*nbSegments)));
        points.push_back(cv::Point(x + rayonExinscrit*cos(theta), y + rayonExinscrit*sin(theta)));
    }
    
    // Ajout du rectangle sur la table
    _table.add_polygon(points);
}

int VisilibityWrapper::nb_obstacles()
{
    //le premier élément de l'environnement est là pour représenter les bords de la table
    return _environment.h() + 1;
}

VisiLibity::Polygon VisilibityWrapper::get_obstacle(int id_polygon)
{
    return _environment[id_polygon];
}

VisilibityWrapper::Exception VisilibityWrapper::build_environment()
{
    // Récupération des obstacles de la table
    vector<VisiLibity::Polygon> obstacles = _table.get_obstacles();
    
    /** évacuation du bruit... **/
    int nb_obstacles = 0;
    for (vector<VisiLibity::Polygon>::iterator polygon = obstacles.begin(); polygon != obstacles.end(); polygon++)
    {
        if (polygon->n() < 3)
            break;
        else
            nb_obstacles++;
        
        /*
        cout << endl << "polygone : " << endl;
        for (int i = 0; i < polygon->n(); i++)
        {
            cout << "(" << (*polygon)[i].x() << ", " << (*polygon)[i].y() << ")" << endl;
        }
        */
    }
    obstacles.resize(nb_obstacles);
    /** ---------------------- **/
    
    
    // Affichage des résultats
    _table.display();

    // Construction de l'environnement
    _environment = VisiLibity::Environment(obstacles);

    // Vérification de la validité
    if (!_environment.is_valid(_epsilon_vis))
    {
        return VisilibityWrapper::ENVIRONMENT_IS_NOT_VALID;
    }
    
    // Construction du graphe de visibilité
    _visibility_graph = VisiLibity::Visibility_Graph(_environment, _epsilon_vis);

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
    
    // Test d'accessibilité du point d'arrivée
    if (end.in(_environment, _epsilon_vis))
        return _environment.shortest_path(start, end, _visibility_graph, _epsilon_vis);
    else
    {
        // On tente de parvenir à un point proche de l'arrivée demandée (sur un hexagone de tolérance)
        for (int i=0;i<6;i++)
            {
                float theta = i*2*PI/6;
                VisiLibity::Point new_end = VisiLibity::Point(x_end + _rayon_tolerance*cos(theta), y_end + _rayon_tolerance*sin(theta));
                if (new_end.in(_environment, _epsilon_vis))
                    // Nouveau point d'arrivé, proche de la consigne 
                    return path(x_start, y_start, new_end.x(), new_end.y());
            }
            
        // Pas de redirection trouvée, on retourne un chemin vide
        VisiLibity::Polyline vide;
        return vide;
    }
}
