import os
import sqlite3
import json

print("=========================================================")
print("     LinkedIn Autonomous Agent - Diagnostic Audit        ")
print("=========================================================")

# 1. Check AppData Directory & Database
db_path = os.path.expandvars(r"%APPDATA%\LinkedInAgent\linkedin_agent.db")
print(f"[1] SQLite Database Path: {db_path}")
if os.path.exists(db_path):
    print("    -> Status: EXISTS")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"    -> Tables Found: {tables}")
        conn.close()
    except Exception as e:
        print(f"    -> Database Error: {e}")
else:
    print("    -> Status: MISSING (Will be auto-created)")

# 2. Check Cookie Persistence
cookie_path = os.path.expandvars(r"%APPDATA%\LinkedInAgent\linkedin_cookies.json")
print(f"\n[2] Cookie Store Path: {cookie_path}")
if os.path.exists(cookie_path):
    print("    -> Status: EXISTS (Authenticated Session Saved)")
    try:
        with open(cookie_path, "r") as f:
            cookies = json.load(f)
            print(f"    -> Stored Cookie Count: {len(cookies)}")
    except Exception as e:
        print(f"    -> Cookie Parse Error: {e}")
else:
    print("    -> Status: MISSING (Run login bridge to authenticate)")

print("=========================================================")
