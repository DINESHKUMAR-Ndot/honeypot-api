# Antigravity Honeypot v3.0 - Architecture Documentation

## 🏗️ System Overview

The Antigravity Honeypot is a stateful, deception-capable AI designed to combat scammers by wasting their time and extracting actionable intelligence. It operates as a high-interaction honeypot that appears as a vulnerable but slightly confused user.

## 🧠 Core Components

### 1. Detection Engine (Behavioral Analysis)
Unlike simple keyword matchers, our engine uses a tiered approach:
-   **Pattern Density**: Measures the frequency of known scam-related regex patterns.
-   **Behavioral Red Flags**: Identifies higher-level intent categories:
    -   *Urgency*: Push for immediate action.
    -   *Fear Tactics*: Threats of legal action or account suspension.
    -   *Verification Fraud*: Requests for sensitive info like OTPs/KYC.
    -   *Financial Bait*: Promises of lottery winnings or refunds.
-   **Confidence Scoring**: A composite metric that triggers the engagement engine when above a 0.3 threshold.

### 2. Engagement Engine (Deception Strategy)
The agent follows a **Stateful Interaction Protocol** to maximize duration and engagement turns:
-   **Dynamic Personas**: Automatically assigns a persona (Elderly, Student, or Professional) based on the session ID to maintain situational consistency.
-   **Investigative Questioning**: Interleaves requests for the scammer's own metadata (Employee ID, Department, Office Location, Case ID) to force the scammer to "invent" details, increasing the cognitive load on them.
-   **Adaptive Stalling**: Implements "human-like" delays and technical confusion (broken screen, slow internet, forgotten passwords) to prolong the session.

### 3. Extraction Engine (Intelligence Harvesting)
Harvests entities from both the current message and the entire conversation history:
-   **Entity Coverage**: Phone Numbers, Bank Accounts, UPI IDs, URLs, Emails, IFSC Codes, and Transaction Amounts.
-   **Multi-Format Export**: Supports both the evaluators' camelCase schema and standard snake_case for maximum compatibility.

## 🔄 Data Flow

1.  **Request Ingress**: Receives POST request with `message` and `conversationHistory`.
2.  **Session Tracking**: Retrieves or initializes session state in memory.
3.  **Scam Validation**: Analyzes behavioral markers and calculates confidence.
4.  **Strategy Selection**: Decision logic chooses between "Investigative Case" or "Stalling Tactic" based on turn count and scammer intensity.
5.  **Intelligence Update**: Updates derived intelligence based on new input.
6.  **Deceptive Response**: Generates a reply with an artificial "typing" delay.
7.  **Callback Submission**: Fires an asynchronous webhook to the reporting endpoint with structured results.

## 🛠️ Technical Stack

-   **Backend**: FastAPI (Python)
-   **Server**: Uvicorn
-   **Threading**: Asynchronous I/O for delays and threaded callbacks for performance.
-   **Deployment**: Ready for Render, Railway, or any containerized environment.

---
*Built with precision for the India AI Impact Buildathon.*
