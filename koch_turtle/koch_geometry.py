import math


def koch_points(start, end, order):
    """Visszaadja a Koch-görbe pontjait bejárási sorrendben."""
    if order < 0:
        raise ValueError('A görbe rendje nem lehet negatív.')

    if order == 0:
        return [start, end]

    x0, y0 = start
    x1, y1 = end

    # Az eredeti szakasz egyharmadának megfelelő vektor.
    dx = (x1 - x0) / 3.0
    dy = (y1 - y0) / 3.0

    first = (x0 + dx, y0 + dy)
    second = (x0 + 2.0 * dx, y0 + 2.0 * dy)

    # Az első osztópontból indulva +60 fokkal elforgatjuk a vektort.
    sin60 = math.sqrt(3.0) / 2.0
    peak = (
        first[0] + 0.5 * dx - sin60 * dy,
        first[1] + sin60 * dx + 0.5 * dy,
    )

    corners = [start, first, peak, second, end]
    points = [start]

    for a, b in zip(corners, corners[1:]):
        segment = koch_points(a, b, order - 1)
        points.extend(segment[1:])

    return points
