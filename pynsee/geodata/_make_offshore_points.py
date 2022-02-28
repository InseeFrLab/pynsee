import math
from shapely.affinity import rotate
from shapely.geometry import Point, LineString

from pynsee.geodata._convert_polygon import _convert_polygon

def _make_offshore_points(center=Point(-1, 47.181903), length=8, pishare=1/17, list_ovdep=['974', '971', '972', '973', '976']):
    
    start = center
    angle = math.pi * (1 - 1.5 * pishare)
    list_points = []
    list_lines = []

    for i in range(len(list_ovdep)):
        
        angle_rotated = angle + math.pi * pishare * i
        end = Point(start.x + length , start.y )
        line = LineString([start, end])
        line = rotate(line, angle_rotated, origin=start, use_radians=True)
       
        list_lines += [line]
        list_points += [_convert_polygon(Point(line.coords[1]))]

    return list_points
