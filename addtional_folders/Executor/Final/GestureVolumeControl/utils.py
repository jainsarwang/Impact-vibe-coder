import numpy as np


def calculate_distance(point1: tuple, point2: tuple) -> float:
    """Calculates the Euclidean distance between two points.

    Args:
        point1 (tuple): The coordinates of the first point (x, y).
        point2 (tuple): The coordinates of the second point (x, y).

    Returns:
        float: The Euclidean distance between the two points.
    """
    return np.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)
