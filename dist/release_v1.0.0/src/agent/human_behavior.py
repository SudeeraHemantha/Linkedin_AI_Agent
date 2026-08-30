import random
import time
import math
from typing import List, Tuple, Optional

def generate_bezier_curve(
    start: Tuple[float, float],
    end: Tuple[float, float],
    num_points: int = 25,
    jitter: float = 1.5,
    overshoot_chance: float = 0.2
) -> List[Tuple[float, float]]:
    """
    Generates a realistic multi-control-point cubic Bezier mouse curve.
    Includes acceleration/deceleration, micro-jitter, and optional random overshoot/correction.
    """
    x0, y0 = start
    x3, y3 = end

    num_points = max(2, num_points)
    distance = math.hypot(x3 - x0, y3 - y0)

    # Scale control point offsets dynamically with distance
    offset_scale = min(120.0, max(20.0, distance * 0.3))
    ctrl_offset1 = random.uniform(-offset_scale, offset_scale)
    ctrl_offset2 = random.uniform(-offset_scale, offset_scale)

    # Optional overshoot target point
    target_x, target_y = x3, y3
    if random.random() < overshoot_chance and distance > 50:
        overshoot_dist = random.uniform(5, 15)
        angle = math.atan2(y3 - y0, x3 - x0)
        target_x = x3 + math.cos(angle) * overshoot_dist
        target_y = y3 + math.sin(angle) * overshoot_dist

    x1 = x0 + (target_x - x0) * random.uniform(0.2, 0.4) + ctrl_offset1
    y1 = y0 + (target_y - y0) * random.uniform(0.2, 0.4) + ctrl_offset2
    x2 = x0 + (target_x - x0) * random.uniform(0.6, 0.8) - ctrl_offset1
    y2 = y0 + (target_y - y0) * random.uniform(0.6, 0.8) - ctrl_offset2

    points = []
    for i in range(num_points):
        # Non-linear t parameter (ease-in ease-out velocity curve)
        step = i / float(num_points - 1)
        # Sine-based easing: slow start, fast middle, decelerate at end
        t = 0.5 * (1.0 - math.cos(step * math.pi))

        # Cubic Bezier evaluation
        xt = ((1 - t) ** 3) * x0 + 3 * ((1 - t) ** 2) * t * x1 + 3 * (1 - t) * (t ** 2) * x2 + (t ** 3) * target_x
        yt = ((1 - t) ** 3) * y0 + 3 * ((1 - t) ** 2) * t * y1 + 3 * (1 - t) * (t ** 2) * y2 + (t ** 3) * target_y

        # Micro-jitter noise (except at start and exact end)
        if 0 < i < num_points - 1:
            xt += random.gauss(0, jitter * 0.3)
            yt += random.gauss(0, jitter * 0.3)

        points.append((round(xt, 2), round(yt, 2)))

    # If overshot, append smooth correction back to exact target
    if (target_x, target_y) != (x3, y3):
        points.append((round(x3, 2), round(y3, 2)))

    return points

def gaussian_delay(mean: float, std_dev: float, min_val: float, max_val: float) -> float:
    """Returns a delay sampled from a Gaussian distribution clamped within [min_val, max_val]."""
    val = random.gauss(mean, std_dev)
    return max(min_val, min(max_val, val))

def random_human_delay(min_sec: float = 0.8, max_sec: float = 2.5):
    """
    Sleeps for a randomized duration drawn from a normal distribution around the midpoint.
    """
    mean = (min_sec + max_sec) / 2.0
    std_dev = max(0.01, (max_sec - min_sec) / 4.0)
    delay = gaussian_delay(mean, std_dev, min_sec, max_sec)
    time.sleep(delay)

def cognitive_pause(min_sec: float = 1.2, max_sec: float = 3.8):
    """Simulates periodic cognitive human thinking pause between form sections or pages."""
    mean = (min_sec + max_sec) / 2.0
    std_dev = (max_sec - min_sec) / 3.0
    delay = gaussian_delay(mean, std_dev, min_sec, max_sec)
    time.sleep(delay)

def random_typing_delay(min_ms: float = 50.0, max_ms: float = 180.0) -> int:
    """Returns random millisecond delay between keystrokes sampled from a Gaussian distribution."""
    mean = (min_ms + max_ms) / 2.0
    std_dev = max(1.0, (max_ms - min_ms) / 4.0)
    delay = gaussian_delay(mean, std_dev, min_ms, max_ms)
    return int(round(delay))


if __name__ == "__main__":
    curve = generate_bezier_curve((100, 100), (500, 400), num_points=10)
    print(f"Generated {len(curve)} Bezier curve trajectory points:")
    for pt in curve:
        print(pt)
