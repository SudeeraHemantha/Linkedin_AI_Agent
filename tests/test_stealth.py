import pytest
from src.agent.human_behavior import (
    generate_bezier_curve,
    gaussian_delay,
    random_human_delay,
    random_typing_delay,
    cognitive_pause
)
from src.agent.stealth_browser import (
    get_stealth_browser_args,
    get_stealth_init_script,
    USER_AGENTS,
    VIEWPORTS
)

def test_bezier_curve_generation_bounds():
    """Verify Bezier curve outputs valid trajectory points within boundary expectations."""
    start = (100.0, 100.0)
    end = (500.0, 400.0)
    num_points = 25

    points = generate_bezier_curve(start, end, num_points=num_points)

    assert len(points) >= num_points
    assert points[0] == (100.0, 100.0)
    assert points[-1] == (500.0, 400.0)

    # Ensure all points are 2-element numeric tuples
    for px, py in points:
        assert isinstance(px, float) or isinstance(px, int)
        assert isinstance(py, float) or isinstance(py, int)

def test_gaussian_delay_clamping():
    """Verify Gaussian delay generator adheres to strict min and max bounds."""
    for _ in range(100):
        delay = gaussian_delay(mean=2.0, std_dev=0.5, min_val=1.0, max_val=3.0)
        assert 1.0 <= delay <= 3.0

def test_random_typing_delay_bounds():
    """Verify millisecond typing latencies fall within reasonable human ranges."""
    for _ in range(50):
        ms = random_typing_delay(35.0, 250.0)
        assert 35 <= ms <= 250


def test_stealth_browser_configurations():
    """Verify Playwright stealth browser flags, scripts, user agents, and viewports."""
    args = get_stealth_browser_args()
    assert "--disable-blink-features=AutomationControlled" in args

    script = get_stealth_init_script()
    assert "navigator" in script
    assert "webdriver" in script
    assert "window.chrome" in script

    assert len(USER_AGENTS) >= 3
    assert len(VIEWPORTS) >= 3
