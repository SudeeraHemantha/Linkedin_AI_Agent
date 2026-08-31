import os
import random
from typing import Optional, Dict, Any, List

def get_stealth_browser_args() -> List[str]:
    """Returns chromium command line arguments engineered for bot detection evasion."""
    return [
        "--disable-blink-features=AutomationControlled",
        "--disable-infobars",
        "--disable-background-networking",
        "--disable-default-apps",
        "--disable-extensions",
        "--disable-gpu",
        "--disable-sync",
        "--disable-translate",
        "--no-first-run",
        "--no-sandbox",
        "--remote-debugging-port=9222"
    ]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0"
]

VIEWPORTS = [
    {"width": 1920, "height": 1080},
    {"width": 1536, "height": 864},
    {"width": 1440, "height": 900},
    {"width": 1366, "height": 768},
    {"width": 1280, "height": 800}
]

def get_stealth_init_script() -> str:
    """JavaScript injected into page context to mask automation flags."""
    return """
    // Overwrite the 'navigator.webdriver' property to prevent detection
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
    });

    // Mock languages and plugins
    Object.defineProperty(navigator, 'languages', {
        get: () => ['en-US', 'en', 'es']
    });

    Object.defineProperty(navigator, 'plugins', {
        get: () => [1, 2, 3, 4, 5]
    });

    // Mock permissions API query
    const originalQuery = window.navigator.permissions.query;
    window.navigator.permissions.query = (parameters) => (
        parameters.name === 'notifications' ?
            Promise.resolve({ state: Notification.permission }) :
            originalQuery(parameters)
    );

    // Mock chrome runtime object
    window.chrome = {
        runtime: {},
        loadTimes: function() {},
        csi: function() {},
        app: {}
    };
    """

async def launch_stealth_context(
    playwright_instance: Any,
    user_data_dir: Optional[str] = None,
    headless: bool = False
):
    r"""
    Launches a Playwright browser context using the user's authentic local Google Chrome
    user profile directory (%LOCALAPPDATA%\Google\Chrome\User Data) to inherit active
    live browser sessions, cookies, and login tokens.
    """

    local_appdata = os.environ.get("LOCALAPPDATA", os.path.join(os.path.expanduser("~"), "AppData", "Local"))
    authentic_chrome_dir = os.path.join(local_appdata, "Google", "Chrome", "User Data")
    appdata = os.environ.get("APPDATA", os.path.expanduser("~"))
    fallback_profile_dir = os.path.join(appdata, "LinkedInAgent", "chrome_user_data")

    if user_data_dir:
        chrome_profile_path = user_data_dir
    elif os.environ.get("CHROME_PROFILE_PATH"):
        chrome_profile_path = os.environ.get("CHROME_PROFILE_PATH")
    elif os.path.exists(authentic_chrome_dir):
        chrome_profile_path = authentic_chrome_dir
    else:
        chrome_profile_path = fallback_profile_dir
        os.makedirs(chrome_profile_path, exist_ok=True)

    print(f"[STEALTH BROWSER CONTEXT] Utilizing Chrome Profile Directory: {chrome_profile_path}")

    args = get_stealth_browser_args()
    
    selected_viewport = random.choice(VIEWPORTS)
    selected_ua = random.choice(USER_AGENTS)

    context = await playwright_instance.chromium.launch_persistent_context(
        user_data_dir=chrome_profile_path,
        headless=headless,
        args=args,
        viewport=selected_viewport,
        user_agent=selected_ua,
        locale="en-US",
        timezone_id="America/New_York"
    )

    # Inject stealth scripts into all new pages
    await context.add_init_script(get_stealth_init_script())
    return context
