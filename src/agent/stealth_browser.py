import os
from typing import Optional, Dict, Any

# Note: playwright module imported dynamically inside functions so backend runs cleanly even if playwright binaries are being downloaded
def get_stealth_browser_args() -> list:
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

def get_stealth_init_script() -> str:
    """JavaScript injected into page context to mask automation flags."""
    return """
    // Overwrite the 'navigator.webdriver' property to prevent detection
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
    });

    // Mock languages and plugins
    Object.defineProperty(navigator, 'languages', {
        get: () => ['en-US', 'en']
    });

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
    """
    Launches a Playwright browser context using either a persistent Chrome profile or a clean context.
    """
    chrome_profile_path = user_data_dir or os.environ.get(
        "CHROME_PROFILE_PATH", 
        os.path.expanduser("~/AppData/Local/Google/Chrome/User Data/Default")
    )
    
    args = get_stealth_browser_args()
    
    if os.path.exists(chrome_profile_path):
        context = await playwright_instance.chromium.launch_persistent_context(
            user_data_dir=chrome_profile_path,
            headless=headless,
            args=args,
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
    else:
        browser = await playwright_instance.chromium.launch(headless=headless, args=args)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )

    # Inject stealth scripts into all new pages
    await context.add_init_script(get_stealth_init_script())
    return context
