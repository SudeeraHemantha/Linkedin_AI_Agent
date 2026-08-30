import random
import time
import math
from typing import List, Tuple

def generate_bezier_curve(
    start: Tuple[float, float],
    end: Tuple[float, float],
    num_points: int = 25
) -> List[Tuple[float, float]]:
    """
    Generates a cubic Bezier curve trajectory between two points with randomized control points
    to simulate natural human mouse movements.
    """
    x0, y0 = start
    x3, y3 = end

    # Ensure num_points is at least 2 to prevent division by zero
    num_points = max(2, num_points)

    # Generate random control points offset from the straight line path
    ctrl_offset1 = random.uniform(-80, 80)
    ctrl_offset2 = random.uniform(-80, 80)

    x1 = x0 + (x3 - x0) * 0.25 + ctrl_offset1
    y1 = y0 + (y3 - y0) * 0.25 + ctrl_offset2
    x2 = x0 + (x3 - x0) * 0.75 - ctrl_offset1
    y2 = y0 + (y3 - y0) * 0.75 - ctrl_offset2

    points = []
    for i in range(num_points):
        t = i / float(num_points - 1)
        # Cubic Bezier formula: B(t) = (1-t)^3*P0 + 3(1-t)^2*t*P1 + 3(1-t)*t^2*P2 + t^3*P3
        xt = ((1 - t) ** 3) * x0 + 3 * ((1 - t) ** 2) * t * x1 + 3 * (1 - t) * (t ** 2) * x2 + (t ** 3) * x3
        yt = ((1 - t) ** 3) * y0 + 3 * ((1 - t) ** 2) * t * y1 + 3 * (1 - t) * (t ** 2) * y2 + (t ** 3) * y3
        points.append((round(xt, 2), round(yt, 2)))

    return points

def random_human_delay(min_sec: float = 0.8, max_sec: float = 2.5):
    """
    Sleeps for a randomized duration drawn from a normal distribution around the midpoint.
    """
    mean = (min_sec + max_sec) / 2.0
    std_dev = max(0.01, (max_sec - min_sec) / 4.0)
    delay = random.gauss(mean, std_dev)
    clamped_delay = max(min_sec, min(max_sec, delay))
    time.sleep(clamped_delay)

def random_typing_delay(min_ms: int = 50, max_ms: int = 180) -> int:
    """Returns random millisecond delay between keystrokes."""
    return random.randint(min_ms, max_ms)

if __name__ == "__main__":
    curve = generate_bezier_curve((100, 100), (500, 400), num_points=10)
    print(f"Generated {len(curve)} Bezier curve trajectory points:")
    for pt in curve:
        print(pt)
