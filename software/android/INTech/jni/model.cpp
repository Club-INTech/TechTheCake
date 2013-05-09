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
		model.insert(pair<int, Point2f>(1, Point(463, 146)));
		model.insert(pair<int, Point2f>(2, Point(430, 150)));
		model.insert(pair<int, Point2f>(3, Point(390, 150)));
		model.insert(pair<int, Point2f>(4, Point(342, 152)));
		model.insert(pair<int, Point2f>(5, Point(298, 151)));
		model.insert(pair<int, Point2f>(6, Point(258, 150)));
		model.insert(pair<int, Point2f>(7, Point(426, 118)));
		model.insert(pair<int, Point2f>(8, Point(383, 121)));
		model.insert(pair<int, Point2f>(9, Point(330, 120)));
		model.insert(pair<int, Point2f>(10, Point(282, 118)));
	}
	else
	{
		model.insert(pair<int, Point2f>(1, Point(42, 150)));
		model.insert(pair<int, Point2f>(2, Point(73, 153)));
		model.insert(pair<int, Point2f>(3, Point(112, 153)));
		model.insert(pair<int, Point2f>(4, Point(157, 153)));
		model.insert(pair<int, Point2f>(5, Point(203, 153)));
		model.insert(pair<int, Point2f>(6, Point(248, 148)));
		model.insert(pair<int, Point2f>(7, Point(73, 119)));
		model.insert(pair<int, Point2f>(8, Point(114, 119)));
		model.insert(pair<int, Point2f>(9, Point(163, 119)));
		model.insert(pair<int, Point2f>(10, Point(214, 117)));
	}

	return model;
}
