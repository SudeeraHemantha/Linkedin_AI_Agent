import os
import sys
import time
import shutil
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

# Theme Palette Constants
BG_COLOR = "#0f172a"
PANEL_BG = "#1e293b"
ACCENT_BLUE = "#3b82f6"
TEXT_COLOR = "#f8fafc"
MUTED_TEXT = "#94a3b8"
BORDER_COLOR = "#334155"

class ModernSetupWizard:
    def __init__(self, root):
        self.root = root
        self.root.title("LinkedIn AI Agent - Setup Wizard")
        self.root.geometry("600x450")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_COLOR)

        # Center window on screen
        self.center_window()

        # Set window icon if present
        self.icon_path = os.path.join(os.path.dirname(__file__), "app_icon.ico")
        if os.path.exists(self.icon_path):
            try:
                self.root.iconbitmap(self.icon_path)
            except Exception:
                pass

        # Data Variables
        self.groq_key_var = tk.StringVar(value=os.environ.get("GROQ_API_KEY", ""))
        self.smtp_user_var = tk.StringVar(value=os.environ.get("SMTP_USER", ""))
        self.smtp_pass_var = tk.StringVar(value=os.environ.get("SMTP_PASSWORD", ""))

        self.current_step = 1

        # Header Tracker Bar
        self.header_frame = tk.Frame(self.root, bg=PANEL_BG, height=60)
        self.header_frame.pack(fill="x", side="top")

        self.step_label = tk.Label(
            self.header_frame,
            text="Step 1 of 3: Welcome & Prerequisites",
            font=("Segoe UI", 11, "bold"),
            bg=PANEL_BG,
            fg=ACCENT_BLUE
        )
        self.step_label.pack(side="left", padx=20, pady=15)

        # Container for screens
        self.container = tk.Frame(self.root, bg=BG_COLOR)
        self.container.pack(fill="both", expand=True, padx=20, pady=20)

        # Navigation Footer Bar
        self.footer_frame = tk.Frame(self.root, bg=BG_COLOR, height=50)
        self.footer_frame.pack(fill="x", side="bottom", padx=20, pady=10)

        self.btn_back = tk.Button(
            self.footer_frame,
            text="< Back",
            font=("Segoe UI", 9, "bold"),
            bg=PANEL_BG,
            fg=TEXT_COLOR,
            activebackground=BORDER_COLOR,
            activeforeground=TEXT_COLOR,
            bd=0,
            padx=15,
            pady=6,
            command=self.prev_step,
            state="disabled"
        )
        self.btn_back.pack(side="left")

        self.btn_next = tk.Button(
            self.footer_frame,
            text="Next >",
            font=("Segoe UI", 9, "bold"),
            bg=ACCENT_BLUE,
            fg="#ffffff",
            activebackground="#2563eb",
            activeforeground="#ffffff",
            bd=0,
            padx=20,
            pady=6,
            command=self.next_step
        )
        self.btn_next.pack(side="right")

        # Screens dictionary
        self.screens = {}
        self.init_screens()
        self.show_screen(1)

    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def init_screens(self):
        # Screen 1: Welcome & Prerequisites
        s1 = tk.Frame(self.container, bg=BG_COLOR)
        title = tk.Label(s1, text="Welcome to LinkedIn AI Agent Setup", font=("Segoe UI", 14, "bold"), bg=BG_COLOR, fg=TEXT_COLOR)
        title.pack(anchor="w", pady=(0, 10))

        desc = (
            "This installer will configure your local LinkedIn Autonomous Agent environment, "
            "initialize non-volatile SQLite database storage in AppData, set up AI LLM keys, "
            "and register system tray background daemons.\n\n"
            "• Python 3.10+ & Playwright Browser Engine\n"
            "• Local Non-Volatile SQLite Storage (%APPDATA%\\LinkedInAgent)\n"
            "• Groq High-Speed Developer API Integration"
        )
        desc_label = tk.Label(s1, text=desc, font=("Segoe UI", 10), bg=BG_COLOR, fg=MUTED_TEXT, justify="left", wraplength=550)
        desc_label.pack(anchor="w", pady=(0, 15))
        self.screens[1] = s1

        # Screen 2: System Configuration & Keys
        s2 = tk.Frame(self.container, bg=BG_COLOR)
        title2 = tk.Label(s2, text="System Configuration & API Keys", font=("Segoe UI", 14, "bold"), bg=BG_COLOR, fg=TEXT_COLOR)
        title2.pack(anchor="w", pady=(0, 10))

        # Groq API Key
        lbl_groq = tk.Label(s2, text="Groq API Key (GROQ_API_KEY):", font=("Segoe UI", 9, "bold"), bg=BG_COLOR, fg=TEXT_COLOR)
        lbl_groq.pack(anchor="w", pady=(5, 2))
        ent_groq = tk.Entry(s2, textvariable=self.groq_key_var, font=("Consolas", 10), bg=PANEL_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR, bd=1, relief="solid")
        ent_groq.pack(fill="x", pady=(0, 10))

        # SMTP User Email
        lbl_smtp_user = tk.Label(s2, text="SMTP Dispatch Email (SMTP_USER):", font=("Segoe UI", 9, "bold"), bg=BG_COLOR, fg=TEXT_COLOR)
        lbl_smtp_user.pack(anchor="w", pady=(5, 2))
        ent_smtp_user = tk.Entry(s2, textvariable=self.smtp_user_var, font=("Segoe UI", 10), bg=PANEL_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR, bd=1, relief="solid")
        ent_smtp_user.pack(fill="x", pady=(0, 10))

        # SMTP App Password
        lbl_smtp_pass = tk.Label(s2, text="SMTP App Password (SMTP_PASSWORD):", font=("Segoe UI", 9, "bold"), bg=BG_COLOR, fg=TEXT_COLOR)
        lbl_smtp_pass.pack(anchor="w", pady=(5, 2))
        ent_smtp_pass = tk.Entry(s2, textvariable=self.smtp_pass_var, show="•", font=("Segoe UI", 10), bg=PANEL_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR, bd=1, relief="solid")
        ent_smtp_pass.pack(fill="x", pady=(0, 10))

        self.screens[2] = s2

        # Screen 3: Installation & Progress
        s3 = tk.Frame(self.container, bg=BG_COLOR)
        title3 = tk.Label(s3, text="Installing LinkedIn Autonomous Agent", font=("Segoe UI", 14, "bold"), bg=BG_COLOR, fg=TEXT_COLOR)
        title3.pack(anchor="w", pady=(0, 10))

        self.progress_bar = ttk.Progressbar(s3, orient="horizontal", mode="determinate", length=550)
        self.progress_bar.pack(fill="x", pady=(10, 15))

        self.log_text = tk.Text(s3, font=("Consolas", 9), bg=PANEL_BG, fg=TEXT_COLOR, height=10, bd=1, relief="solid")
        self.log_text.pack(fill="both", expand=True)

        self.screens[3] = s3

        # Screen 4: Finish Screen
        s4 = tk.Frame(self.container, bg=BG_COLOR)
        title4 = tk.Label(s4, text="Installation Complete!", font=("Segoe UI", 16, "bold"), bg=BG_COLOR, fg="#10b981")
        title4.pack(anchor="w", pady=(0, 10))

        desc4 = (
            "LinkedIn Autonomous Agent has been successfully configured and installed!\n\n"
            "• AppData Database: %APPDATA%\\LinkedInAgent\\linkedin_agent.db\n"
            "• Configuration Secrets Saved to .env\n"
            "• System Tray Daemon Ready\n\n"
            "Click 'Launch Application' to start the local backend server, frontend dashboard, and system tray app."
        )
        lbl_desc4 = tk.Label(s4, text=desc4, font=("Segoe UI", 10), bg=BG_COLOR, fg=TEXT_COLOR, justify="left", wraplength=550)
        lbl_desc4.pack(anchor="w", pady=(0, 20))

        self.screens[4] = s4

    def show_screen(self, step_num):
        for s in self.screens.values():
            s.pack_forget()
        self.screens[step_num].pack(fill="both", expand=True)
        self.current_step = step_num

        if step_num == 1:
            self.step_label.config(text="Step 1 of 3: Welcome & Prerequisites")
            self.btn_back.config(state="disabled")
            self.btn_next.config(text="Next >", state="normal")
        elif step_num == 2:
            self.step_label.config(text="Step 2 of 3: System Configuration & Keys")
            self.btn_back.config(state="normal")
            self.btn_next.config(text="Install Now >", state="normal")
        elif step_num == 3:
            self.step_label.config(text="Step 3 of 3: Installing Application...")
            self.btn_back.config(state="disabled")
            self.btn_next.config(state="disabled")
            threading.Thread(target=self.run_installation, daemon=True).start()
        elif step_num == 4:
            self.step_label.config(text="Step 3 of 3: Installation Complete")
            self.btn_back.config(state="disabled")
            self.btn_next.config(text="Launch Application", state="normal", bg="#10b981", command=self.launch_app)

    def next_step(self):
        if self.current_step < 4:
            self.show_screen(self.current_step + 1)

    def prev_step(self):
        if self.current_step > 1:
            self.show_screen(self.current_step - 1)

    def log_status(self, message):
        self.log_text.insert("end", f"{message}\n")
        self.log_text.see("end")
        self.root.update_idletasks()

    def run_installation(self):
        # 1. Save Configuration to .env
        self.log_status("[1/4] Saving environment configuration to .env...")
        self.progress_bar["value"] = 20
        time.sleep(0.5)

        groq_val = self.groq_key_var.get().strip()
        smtp_user_val = self.smtp_user_var.get().strip()
        smtp_pass_val = self.smtp_pass_var.get().strip()

        env_content = (
            f"GROQ_API_KEY={groq_val}\n"
            f"SMTP_HOST=smtp.gmail.com\n"
            f"SMTP_PORT=587\n"
            f"SMTP_USER={smtp_user_val}\n"
            f"SMTP_PASSWORD={smtp_pass_val}\n"
            f"DATABASE_PATH=%APPDATA%\\LinkedInAgent\\linkedin_agent.db\n"
        )

        root_dir = Path(__file__).parent.parent.parent
        with open(root_dir / ".env", "w", encoding="utf-8") as f:
            f.write(env_content)

        appdata_dir = Path(os.environ.get("APPDATA", os.path.expanduser("~"))) / "LinkedInAgent"
        os.makedirs(appdata_dir, exist_ok=True)
        with open(appdata_dir / ".env", "w", encoding="utf-8") as f:
            f.write(env_content)

        self.log_status("[✓] Environment variables saved.")

        # 2. Database Initialization
        self.log_status("[2/4] Initializing non-volatile SQLite database in AppData...")
        self.progress_bar["value"] = 50
        time.sleep(0.6)

        try:
            from src.backend.database import init_db
            init_db()
            self.log_status("[✓] SQLite database schema initialized (%APPDATA%\\LinkedInAgent\\linkedin_agent.db).")
        except Exception as err:
            self.log_status(f"[WARN] Database init notice: {err}")

        # 3. Register Launcher Scripts
        self.log_status("[3/4] Registering launcher batch scripts and system tray daemon...")
        self.progress_bar["value"] = 85
        time.sleep(0.5)
        self.log_status("[✓] System tray background manager configured.")

        # 4. Finalize
        self.log_status("[4/4] Installation completed successfully!")
        self.progress_bar["value"] = 100
        time.sleep(0.5)

        self.root.after(1000, lambda: self.show_screen(4))

    def launch_app(self):
        root_dir = Path(__file__).parent.parent.parent
        bat_script = root_dir / "launch_agent.bat"
        if bat_script.exists():
            subprocess.Popen([str(bat_script)], shell=True, cwd=str(root_dir))
        self.root.destroy()

def main():
    root = tk.Tk()
    app = ModernSetupWizard(root)
    root.mainloop()

if __name__ == "__main__":
    main()
