# Agentic Honey-Pot API - Antigravity v3.0
## 🎯 India AI Impact Buildathon - Additional Round Optimization

Antigravity v3.0 is a state-of-the-art deception AI designed to detect scammers generically, engage them for up to 10 turns, and extract maximum intelligence (phones, bank accounts, UPI IDs, links, and emails).

---

## 🚀 Core Features (v3.0)

-   **Behavioral Scam Detection**: Moves beyond simple keyword matching to track behavioral red flags like *urgency*, *fear tactics*, *verification fraud*, and *financial bait*.
-   **Stateful Engagement Engine**: Uses a session-aware sequence of **Investigative Questions** (Case ID, Dept ID, Office Address, etc.) and **Stalling Tactics** (Confused persona, technical delays) to reach 8-10 turns.
-   **Multi-Persona Simulation**: Deterministic personas (Elderly, Student, Professional) to maintain 100% believability.
-   **Comprehensive Extraction**: Regex-based entity extraction for Phone Numbers, Bank Accounts, UPI IDs, Phishing Links, and Emails.
-   **Strict Payload Compliance**: Final callback and primary response adhere to the Buildathon's specific structured requirements.

---

## 🛠️ Quick Setup

1.  **Clone & Install**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Environment Setup**:
    Copy `.env.example` to `.env` and set your `API_KEY`.

3.  **Run Locally**:
    ```bash
    python honeypot_api_advanced.py
    ```

4.  **Test Suite**:
    ```bash
    python comprehensive_test.py
    ```

---

## 🧩 How It Works

### 1. Detection Engine (Behavioral Scoring)
Instead of hardcoding "lottery", the engine scores incoming text against categories:
-   **Scam Patterns**: High-level regex matchers.
-   **Red Flags**: Tracks unique behavioral markers across the session history.
-   **Confidence Level**: A composite score (0.0 - 1.0) based on pattern density and unique red flags identified.

### 2. Engagement Engine (Investigation & Stalling)
The agent follows a strategic sequence:
-   **Turns 1-3**: Express interest, ask for "Department Name" or "Employee ID".
-   **Turns 4-6**: Act confused, ask for "Case ID" or "Office Address".
-   **Turns 7-9**: Share "technical difficulties" or "internet issues" while asking for "Official Portal Verification".
-   **Turn 10**: Finalize extraction or stall further.

### 3. Extraction Engine
Monitors the entire `conversationHistory` and current `message` to extract:
-   **Phone Numbers**: Generic Indian formats.
-   **Bank Accounts**: 9-18 digit numeric strings.
-   **UPI IDs**: Comprehensive handle detection.
-   **Phishing Links**: Structured URL extraction.
-   **Email Addresses**: Standard email pattern matching.

---

## 📊 Evaluation Rubric Compliance

Our implementation specifically targets the following points:
-   ✅ **8+ Turns**: Logic ensures at least 10 turns if the scammer persists.
-   ✅ **5+ Questions**: Investigative questions are triggered every 2 turns.
-   ✅ **5+ Red Flags**: Tracks specific behavioral categories.
-   ✅ **180s Duration**: Added artificial (but believable) typing delays and stalling logic.
-   ✅ **Structured Final JSON**: Callback sends the exact fields requested in the rubric.

---

## 📂 Repository Structure

-   `honeypot_api_advanced.py`: The main Antigravity v3.0 core logic.
-   `Architecture.md`: Detailed technical design and flow diagrams.
-   `comprehensive_test.py`: Full simulation of hackathon evaluation scenarios.
-   `requirements.txt`: Python dependencies (FastAPI, Uvicorn, Requests).
-   `.env.example`: Configuration template.
-   `keep_alive.py`: Uptime maintenance script.

---

## 🏆 Success Mindset

This agent is not just a chatbot; it is a **Real-world Deception AI**. It is designed to be slow, inquisitive, and slightly technologically challenged to frustrate scammers into revealing their tools and infrastructure.

*Developed by Antigravity AI for the India AI Impact Buildathon.*
