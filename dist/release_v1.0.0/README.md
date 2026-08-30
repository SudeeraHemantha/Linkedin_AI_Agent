# LinkedIn Autonomous Agent 🤖💼

An enterprise-grade, local-first Desktop & Mobile hybrid platform engineered for automated career management, intelligent resume tailoring, and Playwright stealth job search orchestration.

---

## 🏗 System Architecture Overview

- **/docs/project_design.md**: Comprehensive 4-tier modular blueprint & security specifications.
- **/docs/progression_plan.md**: Phase 1 - 5 master tracking roadmap.
- **/src/backend/**: Python FastAPI server handling local SQLite database, password hashing, JWT auth, mock OTP validation, and LLM hooks.
- **/src/frontend/**: Modern React / Vite SPA with dark glassmorphism styling, left sidebar navigation, and auth controllers.
- **/src/agent/**: Playwright browser stealth launcher, Bezier mouse trajectory calculations, and LinkedIn Easy Apply bot orchestrator.
- **/tests/**: Pytest unit & integration testing suite for auth, OTP, database, and stealth mouse curves.

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- **Python**: 3.9+ installed
- **Node.js**: 18+ installed

### 2. Backend Setup & Run (Port 8000)
```bash
# Install Python dependencies
pip install -r requirements.txt

# Launch FastAPI Local Backend Server
python -m uvicorn src.backend.main:app --host 127.0.0.1 --port 8000 --reload
```
Swagger API documentation will be accessible at: `http://127.0.0.1:8000/docs`

### 3. Frontend Setup & Run (Port 3000)
```bash
# Navigate to frontend folder
cd src/frontend

# Install Node dependencies
npm install

# Start Vite Development Server
npm run dev
```
Open `http://localhost:3000` in your browser.

---

## 📦 Packaging & Installation Wizard

### 1. Build Standalone Release Package
To compile and package the application into a distribution `.zip` archive:
```bash
py build.py
```
This generates the release archive at: `dist/release_v1.0.0.zip`.

### 2. Run Standalone Installation Wizard
To execute the interactive local installation wizard (downloads latest GitHub release asset, decompresses files, initializes local database, and generates desktop startup shortcuts):
```bash
py -m src.installer.wizard
```

---

## 🧪 Running Automated Tests

Run the full Python test suite with pytest:
```bash
py -m pytest tests/
```


---

## 🔐 Local-First Security Principles
1. **Zero External Data Leaks**: Resumes, login sessions, and application metrics are stored locally in SQLite (`linkedin_agent.db`).
2. **Anti-Bot Evasion**: Playwright browser context patches automation flags (`navigator.webdriver`), attaches to Chrome persistent user data profiles, and computes human-like Bezier curves.
