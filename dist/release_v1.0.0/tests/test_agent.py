import pytest
from src.agent.human_behavior import generate_bezier_curve, random_typing_delay
from src.agent.stealth_browser import get_stealth_browser_args, get_stealth_init_script

def test_bezier_curve_generation():
    start_pt = (50.0, 50.0)
    end_pt = (400.0, 300.0)
    num_pts = 20
    
    curve = generate_bezier_curve(start_pt, end_pt, num_points=num_pts)
    
    assert len(curve) == num_pts
    assert curve[0] == (50.0, 50.0)
    assert curve[-1] == (400.0, 300.0)
    
    # Ensure trajectory coordinates are numeric tuples
    for x, y in curve:
        assert isinstance(x, (int, float))
        assert isinstance(y, (int, float))

def test_typing_delay_bounds():
    delay = random_typing_delay(40, 150)
    assert 40 <= delay <= 150

def test_stealth_flags():
    args = get_stealth_browser_args()
    assert "--disable-blink-features=AutomationControlled" in args
    
    script = get_stealth_init_script()
    assert "navigator.webdriver" in script
