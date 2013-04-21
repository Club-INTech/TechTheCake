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
		model.insert(pair<int, Point2f>(1, Point(380, 170)));
		model.insert(pair<int, Point2f>(2, Point(348, 173)));
		model.insert(pair<int, Point2f>(3, Point(308, 178)));
		model.insert(pair<int, Point2f>(4, Point(264, 178)));
		model.insert(pair<int, Point2f>(5, Point(219, 179)));
		model.insert(pair<int, Point2f>(6, Point(178, 179)));
		model.insert(pair<int, Point2f>(7, Point(342, 142)));
		model.insert(pair<int, Point2f>(8, Point(300, 146)));
		model.insert(pair<int, Point2f>(9, Point(250, 146)));
		model.insert(pair<int, Point2f>(10, Point(201, 144)));
	}
	else
	{
		model.insert(pair<int, Point2f>(1, Point(115, 111)));
		model.insert(pair<int, Point2f>(2, Point(146, 114)));
		model.insert(pair<int, Point2f>(3, Point(186, 114)));
		model.insert(pair<int, Point2f>(4, Point(232, 116)));
		model.insert(pair<int, Point2f>(5, Point(278, 114)));
		model.insert(pair<int, Point2f>(6, Point(322, 112)));
		model.insert(pair<int, Point2f>(7, Point(148, 80)));
		model.insert(pair<int, Point2f>(8, Point(188, 81)));
		model.insert(pair<int, Point2f>(9, Point(240, 81)));
		model.insert(pair<int, Point2f>(10, Point(290, 80)));
	}

	return model;
}
