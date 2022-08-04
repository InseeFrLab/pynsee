import math
import warnings
from shapely.affinity import rotate
from shapely.geometry import Point, LineString


def _make_offshore_points(
    center=Point(-1, 47.181903),
    radius=8,
    angle=1 / 17,
    startAngle=math.pi * (1 - 1.5 * 1 / 17),
    list_ovdep=["974", "971", "972", "973", "976"],
):

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        list_points = []

        for i in range(len(list_ovdep)):

            angle_rotated = startAngle + angle * i
            end = Point(center.x + radius, center.y)
            line = LineString([center, end])
            line = rotate(line, angle_rotated, origin=center, use_radians=True)

            list_points += [Point(line.coords[1])]

        return list_points
