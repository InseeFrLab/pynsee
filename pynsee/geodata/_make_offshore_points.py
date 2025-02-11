import math
import warnings
from typing import Optional

from shapely.affinity import rotate
from shapely.geometry import Point, LineString


def _make_offshore_points(
    center: Optional[Point] = None,
    radius: float = 8,
    angle: float = 1 / 17,
    startAngle: float = math.pi * (1 - 1.5 * 1 / 17),
    list_ovdep: tuple[str, ...] = ("974", "971", "972", "973", "976"),
) -> list[Point]:
    """Create the center points for French overseas departments"""
    center = center or Point(-1, 47.181903)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        list_points = []

        for i in range(len(list_ovdep)):

            angle_rotated = startAngle + angle * i
            end = Point(center.x + radius, center.y)
            line = LineString([center, end])
            line = rotate(line, angle_rotated, origin=center, use_radians=True)

            list_points.append(Point(line.coords[1]))

        return list_points
