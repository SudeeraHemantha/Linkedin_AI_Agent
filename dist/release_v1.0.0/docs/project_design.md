# LinkedIn Autonomous Agent - System Design & Architecture Blueprint

## Executive Overview
**LinkedIn Autonomous Agent** is an enterprise-grade, local-first Desktop & Mobile hybrid platform engineered for automated, intelligent career management and job application orchestration. Designed with privacy, resilience, and stealth at its core, all sensitive credentials, resumes, and browsing profiles remain 100% client-side.

---

## 4-Tier Modular Architecture

```mermaid
graph TD
    subgraph Tier 1: Presentation Layer (SPA Frontend)
        React[React / Vite SPA]
        Sidebar[Responsive Left Navigation]
        AuthView[Auth & OTP Modals]
        Dashboard[Analytics & Agent Monitor]
    end

    subgraph Tier 2: Orchestration & Authentication Layer (Backend API)
        FastAPI[Python FastAPI Server]
        AuthCtrl[Authentication & Security Controller]
        OTPMgr[OTP Verification Engine]
        LLMHooks[AI Resume & Cover Letter Engine]
    end

    subgraph Tier 3: Autonomous Agent Execution Engine
        Playwright[Playwright Engine]
        Stealth[Anti-Detection Stealth Module]
        HumanSim[Human Behavior & Bezier Simulation]
        LinkedInBot[LinkedIn Easy Apply Orchestrator]
    end

    subgraph Tier 4: Storage & Cryptographic Layer
        SQLite[(SQLite / SQLCipher Database)]
        LocalCreds[AES-256 Encrypted Credential Vault]
        ChromeProfile[Local Chrome Persistent Context]
    end

    React <-->|REST API / WebSockets| FastAPI
    FastAPI <--> SQLite
    FastAPI <--> LLMHooks
    FastAPI <--> Playwright
    Playwright --> Stealth
    Playwright --> HumanSim
    Playwright --> LinkedInBot
    LinkedInBot <--> ChromeProfile
```

### 1. Tier 1: Presentation Layer (`/src/frontend/`)
- **Technology**: React, Vite, CSS Dark Glassmorphism Design System.
- **Responsibilities**:
  - SPA Navigation via Left Sidebar.
  - Interactive Resume Dropzone & Manual Builder.
  - Real-time Auto-Pilot Agent execution tracking and telemetry.
  - Secure authentication views (Login, Register with OTP, Password Reset).

### 2. Tier 2: Orchestration & Backend Layer (`/src/backend/`)
- **Technology**: Python FastAPI, Uvicorn, Pydantic, PyJWT, Passlib.
- **Responsibilities**:
  - Secure user authentication, password hashing (PBKDF2/SHA256), and JWT sessions.
  - Enterprise Mock OTP generation, dispatching simulation, and validation.
  - SQLite database management and query execution.
  - LLM Integration hooks for tailoring resumes to job descriptions.

### 3. Tier 3: Autonomous Agent Engine (`/src/agent/`)
- **Technology**: Python Playwright, Custom Stealth Helpers, NumPy/SciPy Bezier Math.
- **Responsibilities**:
  - Attachment to local Chrome user profile (bypassing re-login challenges).
  - Human-like interaction generation: randomized Gaussian delays and cubic Bezier curve mouse movement trajectories.
  - Automated job search parsing and Easy Apply form submission.

### 4. Tier 4: Storage & Security Layer
- **Technology**: SQLite / SQLCipher (`linkedin_agent.db`), Local Storage.
- **Responsibilities**:
  - Local persistence of user profile, resumes, applied job logs, and agent audit trails.
  - Zero cloud dependency for personal user data.

---

## Security & Privacy Protocols
1. **Local-First Data Isolation**: No user credentials or job application data are stored on external servers.
2. **Encrypted Storage**: Sensitive session tokens and passwords stored using PBKDF2 with unique salt.
3. **Mock Enterprise OTP Flow**: Two-factor verification step during registration to simulate enterprise security standards.
4. **Stealth Evasion**: Playwright patches navigator flags (`navigator.webdriver` removal, realistic browser fingerprinting, random viewports).

---

## Left Sidebar Feature Matrix

| Feature | Description | Status |
| :--- | :--- | :--- |
| **Profile** | User personal information, contact info, and career preferences. | Core Integrated |
| **Resume Dropzone** | Drag-and-drop parser for PDF/DOCX resumes. | Core Integrated |
| **Manual Resume Builder**| Structured form builder for experience, skills, and education. | Core Integrated |
| **AI Tailor & Generator**| LLM prompt interface to generate custom resumes & cover letters per job. | Core Integrated |
| **Auto-Pilot Agent** | Control center to configure, launch, and pause the Playwright autonomous bot. | Core Integrated |
| **Live Tracker** | Real-time analytics table showing applied jobs, response rates, and statuses. | Core Integrated |
| **Settings** | Configuration for local Chrome profile paths, LLM API keys, and delay sliders. | Core Integrated |

---

## Development Status
- **Phase 1 (Foundation & System Design)**: ✅ COMPLETE
- **Phase 2 (Core Module Development)**: 🚀 IN PROGRESS
