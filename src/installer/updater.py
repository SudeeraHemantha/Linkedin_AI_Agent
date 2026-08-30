import os
import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional

GITHUB_REPO = "SudeeraHemantha/Linkedin_AI_Agent"
RELEASES_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"

class GitHubReleaseUpdater:
    def __init__(self, current_version: str = "1.0.0"):
        self.current_version = current_version
        self.repo = GITHUB_REPO

    def fetch_latest_release_info(self) -> Dict[str, Any]:
        """Fetches latest release metadata from GitHub API."""

        headers = {
            "User-Agent": "LinkedIn-Autonomous-Agent-Installer/1.0",
            "Accept": "application/vnd.github.v3+json"
        }
        req = urllib.request.Request(RELEASES_API_URL, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    return {
                        "status": "success",
                        "tag_name": data.get("tag_name", "v1.0.0"),
                        "name": data.get("name", "LinkedIn Agent Release"),
                        "zipball_url": data.get("zipball_url"),
                        "assets": data.get("assets", []),
                        "published_at": data.get("published_at")
                    }
        except urllib.error.HTTPError as e:
            # Fallback mock for local sandbox environment when GitHub API rate-limits or release is draft
            return {
                "status": "fallback",
                "tag_name": "v1.0.0",
                "name": "LinkedIn Agent v1.0.0 Sandbox Release",
                "download_url": f"https://github.com/{GITHUB_REPO}/archive/refs/heads/main.zip"
            }
        except Exception as e:
            return {
                "status": "fallback",
                "tag_name": "v1.0.0",
                "name": "LinkedIn Agent v1.0.0 Local Release",
                "message": str(e)
            }

        return {
            "status": "fallback",
            "tag_name": "v1.0.0",
            "name": "LinkedIn Agent v1.0.0 Local Release",
            "message": "Failed to retrieve release payload."
        }


    def download_release_archive(self, download_url: str, output_path: str) -> bool:
        """Downloads the release zip archive file to output_path."""
        headers = {"User-Agent": "LinkedIn-Autonomous-Agent-Installer/1.0"}
        req = urllib.request.Request(download_url, headers=headers)
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with urllib.request.urlopen(req, timeout=30) as response, open(output_path, 'wb') as out_file:
                out_file.write(response.read())
            return os.path.exists(output_path) and os.path.getsize(output_path) > 0
        except Exception as e:
            print(f"[UPDATER ERROR] Archive download failed: {e}")
            return False

if __name__ == "__main__":
    updater = GitHubReleaseUpdater()
    info = updater.fetch_latest_release_info()
    print("Latest Release Metadata:", json.dumps(info, indent=2))
