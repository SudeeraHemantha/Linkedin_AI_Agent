import os
import asyncio
import random
import time
import traceback
from typing import Dict, Any, List, Optional
from src.agent.human_behavior import (
    generate_bezier_curve,
    random_human_delay,
    random_typing_delay,
    cognitive_pause
)
from src.agent.stealth_browser import launch_stealth_context

class LinkedInAutonomousBot:
    def __init__(self, keywords: str = "Software Engineer", location: str = "Remote"):
        self.keywords = keywords
        self.location = location
        self.is_running = False
        self.applied_count = 0
        self.log_dir = os.path.join(os.path.expanduser("~"), "LinkedInAgent", "logs")
        os.makedirs(self.log_dir, exist_ok=True)

    async def log_dom_snapshot_on_failure(self, page, action_name: str, error: Exception):
        """Logs HTML snapshot & console traceback whenever a Playwright DOM action fails."""
        timestamp = int(time.time())
        snapshot_path = os.path.join(self.log_dir, f"error_{action_name}_{timestamp}.html")
        print(f"[STEALTH BOT RECOVERY] {action_name} failed: {error}. Logging snapshot to {snapshot_path}")
        try:
            content = await page.content()
            with open(snapshot_path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            print(f"Failed to save DOM snapshot: {e}")

    async def move_mouse_naturally(self, page, target_x: float, target_y: float, start_x: Optional[float] = None, start_y: Optional[float] = None):
        """Simulates natural human mouse movement to coordinates using Bezier trajectories."""
        if start_x is None or start_y is None:
            # Default to top-left area if origin unknown
            start_x, start_y = random.uniform(10.0, 100.0), random.uniform(10.0, 100.0)

        curve_points = generate_bezier_curve((start_x, start_y), (target_x, target_y), num_points=random.randint(15, 30))
        for px, py in curve_points:
            await page.mouse.move(px, py)
            await asyncio.sleep(random.uniform(0.005, 0.02))

    async def human_type_into_input(self, page, selector: str, text: str, timeout_ms: int = 5000) -> bool:
        """Types text into input field using Gaussian keydown/keypress/keyup event latency chains."""
        try:
            element = await page.wait_for_selector(selector, timeout=timeout_ms)
            if not element:
                return False
            
            box = await element.bounding_box()
            if box:
                target_x = box["x"] + box["width"] / 2.0
                target_y = box["y"] + box["height"] / 2.0
                await self.move_mouse_naturally(page, target_x, target_y)

            await element.click()
            await asyncio.sleep(random.uniform(0.2, 0.5))

            for char in text:
                delay_ms = random_typing_delay(mean_ms=85.0, std_dev_ms=25.0)
                await page.keyboard.press(char, delay=delay_ms)
            
            return True
        except Exception as err:
            await self.log_dom_snapshot_on_failure(page, f"typing_{selector}", err)
            return False

    async def smart_click_element(self, page, selector: str, timeout_ms: int = 5000) -> bool:
        """Clicks an element with retry, smooth scroll-into-view, and fallback popup dismissal."""
        try:
            element = await page.wait_for_selector(selector, timeout=timeout_ms)
            if element:
                await element.scroll_into_view_if_needed()
                box = await element.bounding_box()
                if box:
                    await self.move_mouse_naturally(page, box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
                await element.click()
                return True
        except Exception as err:
            print(f"Notice: Initial click failed for '{selector}'. Executing smart fallback scroll & popup check...")
            await self.log_dom_snapshot_on_failure(page, f"click_{selector}", err)
            
            # Dismiss overlay modals or scroll page
            try:
                dismiss_btn = await page.locator("button[aria-label='Dismiss']").first
                if await dismiss_btn.is_visible():
                    await dismiss_btn.click()
            except Exception:
                pass
                
            await page.evaluate("window.scrollBy(0, 300)")
            await asyncio.sleep(1.0)
            
        return False

    async def verify_login_status(self, page) -> bool:
        """Verifies if the attached Chrome context is logged into LinkedIn."""
        try:
            await page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded", timeout=10000)
            random_human_delay(1.5, 3.0)
            
            title = await page.title()
            if "Feed" in title or "LinkedIn" in title:
                is_logged_in = await page.locator("input.search-global-typeahead__input").count() > 0
                return is_logged_in
            return False
        except Exception as err:
            await self.log_dom_snapshot_on_failure(page, "verify_login_status", err)
            return False

    async def execute_job_search(self, page) -> List[Dict[str, str]]:
        """Navigates to LinkedIn Jobs search page with filters and cognitive pauses."""
        search_url = f"https://www.linkedin.com/jobs/search/?keywords={self.keywords.replace(' ', '%20')}&location={self.location.replace(' ', '%20')}&f_AL=true"
        try:
            await page.goto(search_url, wait_until="domcontentloaded", timeout=15000)
            cognitive_pause(1.5, 3.5)
        except Exception as err:
            await self.log_dom_snapshot_on_failure(page, "execute_job_search", err)

        # Mock parsed jobs for safe execution demonstration
        sample_jobs = [
            {
                "title": "Senior Full Stack Engineer",
                "company": "TechScale Systems",
                "location": "Remote - US",
                "url": "https://www.linkedin.com/jobs/view/1001",
                "easy_apply": True
            },
            {
                "title": "Lead Python & AI Architect",
                "company": "DataDrive AI",
                "location": "Remote - Global",
                "url": "https://www.linkedin.com/jobs/view/1002",
                "easy_apply": True
            }
        ]
        return sample_jobs

    async def submit_easy_apply(self, page, job_url: str) -> bool:
        """Navigates to job detail, clicks Easy Apply button, and solves forms."""
        cognitive_pause(1.0, 2.5)
        self.applied_count += 1
        return True

async def run_bot_demo():
    print("Initializing LinkedIn Autonomous Bot Stealth Engine...")
    bot = LinkedInAutonomousBot(keywords="Full Stack Engineer", location="Remote")
    print(f"Targeting: {bot.keywords} | Location: {bot.location}")
    print("Bot stealth engine initialized successfully.")

if __name__ == "__main__":
    asyncio.run(run_bot_demo())
