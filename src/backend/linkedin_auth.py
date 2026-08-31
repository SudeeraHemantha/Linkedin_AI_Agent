import os
import json
import asyncio
import time
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/linkedin", tags=["LinkedIn Session Auth"])

def get_cookies_file_path() -> str:
    """Resolves path for non-volatile LinkedIn cookies JSON storage."""
    appdata = os.environ.get("APPDATA", os.path.expanduser("~"))
    dir_path = os.path.join(appdata, "LinkedInAgent")
    os.makedirs(dir_path, exist_ok=True)
    return os.path.join(dir_path, "linkedin_cookies.json")

def load_stored_cookies() -> list:
    """Loads saved LinkedIn cookies array from JSON file."""
    cookie_path = get_cookies_file_path()
    if os.path.exists(cookie_path):
        try:
            with open(cookie_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as err:
            print(f"[LINKEDIN COOKIE LOAD WARN] Failed to parse cookies file: {err}")
    return []

def save_stored_cookies(cookies: list) -> bool:
    """Saves LinkedIn cookies array to JSON file."""
    cookie_path = get_cookies_file_path()
    try:
        with open(cookie_path, "w", encoding="utf-8") as f:
            json.dump(cookies, f, indent=2)
        return True
    except Exception as err:
        print(f"[LINKEDIN COOKIE SAVE ERROR] Failed to save cookies file: {err}")
        return False

@router.get("/status")
def get_linkedin_connection_status():
    """Returns whether active saved LinkedIn cookies exist."""
    cookies = load_stored_cookies()
    has_session = len(cookies) > 0
    return {
        "status": "connected" if has_session else "disconnected",
        "cookie_count": len(cookies),
        "cookies_path": get_cookies_file_path()
    }

async def launch_headed_login_bridge(timeout_seconds: int = 120) -> Dict[str, Any]:
    """
    Launches a headed Playwright Chromium browser session, navigates to LinkedIn login page,
    waits for manual user login, and extracts session cookies upon authentication.
    """
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="Playwright is not installed. Please install playwright package to connect LinkedIn."
        )

    try:
        async with async_playwright() as p:
            # Launch headed browser context for user interaction
            browser = await p.chromium.launch(
                headless=False,
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
            )
            context = await browser.new_context(
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            )
            page = await context.new_page()

            print("[LINKEDIN AUTH BRIDGE] Navigating to https://www.linkedin.com/login...")
            await page.goto("https://www.linkedin.com/login", wait_until="domcontentloaded")

            start_time = time.time()
            is_authenticated = False

            # Poll for successful login redirect or feed element presence
            while time.time() - start_time < timeout_seconds:
                try:
                    current_url = page.url
                    # Check for redirect to feed or presence of global nav / search input
                    if "feed" in current_url or "check/challenge" in current_url:
                        if "feed" in current_url:
                            is_authenticated = True
                            break
                    
                    nav_count = await page.locator("div.global-nav, input.search-global-typeahead__input").count()
                    if nav_count > 0:
                        is_authenticated = True
                        break
                except Exception:
                    pass

                await asyncio.sleep(1.5)

            if is_authenticated:
                # Capture and persist session cookies
                cookies = await context.cookies()
                saved = save_stored_cookies(cookies)
                await browser.close()
                if saved:
                    return {
                        "status": "connected",
                        "message": "LinkedIn session cookies successfully captured and stored.",
                        "cookie_count": len(cookies)
                    }
                else:
                    return {
                        "status": "error",
                        "message": "Failed to save captured session cookies to disk."
                    }
            else:
                await browser.close()
                return {
                    "status": "error",
                    "message": "LinkedIn login timed out or window closed before completing authentication."
                }
    except Exception as err:
        print(f"[LINKEDIN AUTH BRIDGE ERROR] {err}")
        return {
            "status": "error",
            "message": f"Interactive authentication bridge error: {str(err)}"
        }

@router.post("/connect")
async def connect_linkedin_account():
    """
    Triggers headed Playwright browser for interactive user LinkedIn login
    and saves session cookies into non-volatile storage.
    """
    res = await launch_headed_login_bridge(timeout_seconds=120)
    if res.get("status") == "error":
        raise HTTPException(status_code=400, detail=res.get("message"))
    return res
