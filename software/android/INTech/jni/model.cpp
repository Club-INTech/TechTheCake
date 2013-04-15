#include "model.h"
#include "ball.h"

#include <iostream>

using namespace cv;
using namespace std;

map<int, Point2f> Model::getRepartitionModel(char color)
{
	std::map<int, cv::Point2f> model;

	if (color == 'r')
	{
		model.insert(pair<int, Point2f>(1, Point(180, 90)));
		model.insert(pair<int, Point2f>(2, Point(206, 92)));
		model.insert(pair<int, Point2f>(3, Point(237, 95)));
		model.insert(pair<int, Point2f>(4, Point(274, 97)));
		model.insert(pair<int, Point2f>(5, Point(311, 97)));
		model.insert(pair<int, Point2f>(6, Point(346, 95)));
		model.insert(pair<int, Point2f>(7, Point(209, 55)));
		model.insert(pair<int, Point2f>(8, Point(241, 58)));
		model.insert(pair<int, Point2f>(9, Point(283, 59)));
		model.insert(pair<int, Point2f>(10, Point(322, 59)));
	}
	else
	{
		model.insert(pair<int, Point2f>(1, Point(180, 90)));
		model.insert(pair<int, Point2f>(2, Point(206, 92)));
		model.insert(pair<int, Point2f>(3, Point(237, 95)));
		model.insert(pair<int, Point2f>(4, Point(274, 97)));
		model.insert(pair<int, Point2f>(5, Point(311, 97)));
		model.insert(pair<int, Point2f>(6, Point(346, 95)));
		model.insert(pair<int, Point2f>(7, Point(209, 55)));
		model.insert(pair<int, Point2f>(8, Point(241, 58)));
		model.insert(pair<int, Point2f>(9, Point(283, 59)));
		model.insert(pair<int, Point2f>(10, Point(322, 59)));
	}

	return model;
}

