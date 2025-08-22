"""Utility helpers for calibration and mapping."""

from typing import List, Tuple


class Linearizer:
    """Piecewise-linear mapping built from (x, y) pairs sorted by x."""

    def __init__(self, points: List[Tuple[float, float]]):
        if len(points) < 2:
            raise ValueError("At least two points required")
        self.points = sorted(points, key=lambda p: p[0])

    def __call__(self, x: float) -> float:
        pts = self.points
        if x <= pts[0][0]:
            return pts[0][1]
        if x >= pts[-1][0]:
            return pts[-1][1]
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            if x0 <= x <= x1:
                # linear interpolation
                t = (x - x0) / (x1 - x0)
                return y0 + t * (y1 - y0)
        return pts[-1][1]
