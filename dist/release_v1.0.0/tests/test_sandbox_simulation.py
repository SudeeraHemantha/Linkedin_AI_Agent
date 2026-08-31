import pytest
import asyncio
from src.agent.linkedin_bot import LinkedInAutonomousBot
from src.agent.human_behavior import generate_bezier_curve, random_typing_delay

def test_bot_sandbox_initialization():
    async def _test():
        bot = LinkedInAutonomousBot(keywords="AI Engineer", location="Remote - US")
        assert bot.keywords == "AI Engineer"
        assert bot.location == "Remote - US"
        assert bot.is_running is False
        assert bot.applied_count == 0
    asyncio.run(_test())

def test_bot_job_search_sandbox_execution():
    async def _test():
        bot = LinkedInAutonomousBot(keywords="Full Stack Architect", location="Remote")
        
        class MockLocator:
            def __init__(self, text="", href="", count_val=1):
                self._text = text
                self._href = href
                self._count_val = count_val

            @property
            def first(self):
                return self

            async def count(self):
                return self._count_val

            async def inner_text(self):
                return self._text

            async def get_attribute(self, name):
                return self._href

        class MockCard:
            def locator(self, sel):
                if "title" in sel:
                    return MockLocator(text="Full Stack Architect")
                elif "subtitle" in sel:
                    return MockLocator(text="Tech Enterprise")
                elif "location" in sel:
                    return MockLocator(text="Remote")
                elif "link" in sel:
                    return MockLocator(href="https://www.linkedin.com/jobs/view/123456")
                return MockLocator()

        class SandboxPage:
            async def goto(self, url, wait_until=None, timeout=None):
                pass
            
            def locator(self, selector):
                class CardListLocator:
                    async def all(self):
                        return [MockCard(), MockCard()]
                return CardListLocator()

        page = SandboxPage()
        jobs = await bot.execute_job_search(page)
        
        assert isinstance(jobs, list)
        assert len(jobs) >= 2
        assert jobs[0]["easy_apply"] is True
        assert "title" in jobs[0]
        assert "company" in jobs[0]
    asyncio.run(_test())


def test_bot_easy_apply_submission_sandbox():
    async def _test():
        bot = LinkedInAutonomousBot(keywords="Full Stack Architect", location="Remote")
        
        class SandboxPage:
            pass
            
        page = SandboxPage()
        success = await bot.submit_easy_apply(page, "https://www.linkedin.com/jobs/view/9999")
        
        assert success is True
        assert bot.applied_count == 1
    asyncio.run(_test())
