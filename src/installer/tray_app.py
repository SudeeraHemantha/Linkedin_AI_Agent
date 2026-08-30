import sys
import os
import time
import threading
import webbrowser
from typing import Dict, Any, Optional

try:
    import pystray
    from PIL import Image, ImageDraw
    PYSTRAY_AVAILABLE = True
except ImportError:
    PYSTRAY_AVAILABLE = False

class LinkedInAgentTrayApp:
    def __init__(self, dashboard_url: str = "http://localhost:3000"):
        self.dashboard_url = dashboard_url
        self.is_running = False
        self.worker_active = True
        self.icon = None
        self.worker_thread = None

    def create_default_icon_image(self):
        """Generates a clean 64x64 PIL icon image for system tray."""
        if not PYSTRAY_AVAILABLE:
            return None
        image = Image.new('RGBA', (64, 64), (10, 102, 194, 255))
        draw = ImageDraw.Draw(image)
        # Draw "in" logo text box
        draw.rectangle([14, 14, 50, 50], fill=(255, 255, 255, 255))
        draw.rectangle([20, 20, 44, 44], fill=(10, 102, 194, 255))
        return image

    def open_dashboard(self, icon=None, item=None):
        """Opens default browser to local frontend dashboard."""
        print(f"[SYSTEM TRAY] Opening dashboard URL: {self.dashboard_url}")
        webbrowser.open(self.dashboard_url)

    def get_worker_status_text(self, item=None) -> str:
        """Returns current worker status string."""
        return f"Worker Status: {'ACTIVE' if self.worker_active else 'IDLE'}"

    def toggle_autonomous_runner(self, icon=None, item=None):
        """Toggles background autonomous worker runner state."""
        self.worker_active = not self.worker_active
        print(f"[SYSTEM TRAY] Autonomous runner toggled: Active = {self.worker_active}")
        if self.icon:
            self.icon.update_menu()

    def quit_application(self, icon=None, item=None):
        """Safely shuts down system tray and application processes."""
        print("[SYSTEM TRAY] Application shutdown requested.")
        self.is_running = False
        self.worker_active = False
        if self.icon:
            self.icon.stop()

    def build_pystray_menu(self):
        """Builds pystray Menu items."""
        if not PYSTRAY_AVAILABLE:
            return None
        return pystray.Menu(
            pystray.MenuItem("LinkedIn Autonomous Agent", None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Open Dashboard (http://localhost:3000)", self.open_dashboard),
            pystray.MenuItem(lambda item: self.get_worker_status_text(), None, enabled=False),
            pystray.MenuItem(lambda item: "Pause Autonomous Runner" if self.worker_active else "Resume Autonomous Runner", self.toggle_autonomous_runner),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit Application", self.quit_application)
        )

    def run_tray_icon(self):
        """Launches tray icon loop."""
        self.is_running = True
        if PYSTRAY_AVAILABLE:
            img = self.create_default_icon_image()
            menu = self.build_pystray_menu()
            self.icon = pystray.Icon("LinkedInAgent", img, "LinkedIn Autonomous Agent", menu)
            self.icon.run()
        else:
            print("[SYSTEM TRAY INFO] pystray/PIL not installed. Running headless tray app wrapper.")
            while self.is_running:
                time.sleep(1)

if __name__ == "__main__":
    tray_app = LinkedInAgentTrayApp()
    tray_app.run_tray_icon()
