# -*- coding: utf-8 -*-
from math import sin, cos, sqrt, atan2, radians

def _distance(point1, point2):
    # see https://stackoverflow.com/questions/19412462/getting-distance-between-two-points-based-on-latitude-longitude
    
    # approximate radius of earth in km
    R = 6373.0
    
    lat1 = radians(point1[1])
    lon1 = radians(point1[0])
    lat2 = radians(point2[1])
    lon2 = radians(point2[0])
    
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    distance = R * c
    
    return distance
