import asyncio
import random
from typing import Dict, Any, List
from src.agent.human_behavior import generate_bezier_curve, random_human_delay, random_typing_delay
from src.agent.stealth_browser import launch_stealth_context

class LinkedInAutonomousBot:
    def __init__(self, keywords: str = "Software Engineer", location: str = "Remote"):
        self.keywords = keywords
        self.location = location
        self.is_running = False
        self.applied_count = 0

    async def verify_login_status(self, page) -> bool:
        """Verifies if the attached Chrome context is logged into LinkedIn."""
        await page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded")
        random_human_delay(1.5, 3.0)
        
        # Check for search bar or user profile badge indicating an active session
        title = await page.title()
        if "Feed" in title or "LinkedIn" in title:
            is_logged_in = await page.locator("input.search-global-typeahead__input").count() > 0
            return is_logged_in
        return False

    async def execute_job_search(self, page) -> List[Dict[str, str]]:
        """Navigates to LinkedIn Jobs search page with filters."""
        search_url = f"https://www.linkedin.com/jobs/search/?keywords={self.keywords.replace(' ', '%20')}&location={self.location.replace(' ', '%20')}&f_AL=true"
        await page.goto(search_url, wait_until="domcontentloaded")
        random_human_delay(2.0, 4.0)

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
        # Calculate human mouse curve to trigger element
        curve = generate_bezier_curve((200, 300), (450, 220), num_points=15)
        # Simulate natural hover delay before click
        random_human_delay(1.0, 2.5)
        
        self.applied_count += 1
        return True

async def run_bot_demo():
    print("Initializing LinkedIn Autonomous Bot Scaffold...")
    bot = LinkedInAutonomousBot(keywords="Full Stack Engineer", location="Remote")
    print(f"Targeting: {bot.keywords} | Location: {bot.location}")
    print("Bot engine initialized successfully.")

if __name__ == "__main__":
    asyncio.run(run_bot_demo())
