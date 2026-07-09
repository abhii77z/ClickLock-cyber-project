# 🛡️ Browser Ghost Click Attack Defender: Technical Documentation

## 1. Project Overview
The **Browser Ghost Click Attack Defender** is a client-side security system designed to detect and prevent ghost-click (click-jacking) attacks. It operates by monitoring behavioral anomalies, detecting invisible overlays, and enforcing a "DOM Freeze" window during user interactions to ensure the legitimacy of every click.

---

## 2. Core Objectives
*   **Behavioral Detection:** Monitor sudden DOM changes specifically near the user's cursor.
*   **DOM Integrity:** Implement a "Freeze" period during `mousedown` events to prevent last-second element swaps.
*   **Forensic Analysis:** Identify and log the specific ID/Class of malicious elements using stack analysis.
*   **Prevention:** Block suspicious events before they execute malicious actions.

---

## 3. System Architecture
The project follows a **Flask-based Client-Server** architecture:
*   **Frontend (HTML/JS):** The "Defender" script runs in the browser, intercepting events and performing heuristic analysis.
*   **Backend (Python/Flask):** Processes security logs, manages statistical data, and serves the administrative dashboard.
*   **Database:** Stores attack logs, legitimate interaction counts, and daily defense statistics.

---

## 4. Key Security Features (Detection Logic)

### A. Proactive Mutation Monitoring
Uses a `MutationObserver` to watch for `childList` and `attribute` changes.
*   **Logic:** If a DOM change occurs within a 10px radius of a stationary cursor, it is flagged as a potential attack preparation.
*   **Target:** Catches scripts that move malicious buttons under the user's mouse right before a click.

### B. DOM "Freeze" Mechanism
The system enforces a strict "Freeze" window the moment a user presses down on the mouse.
*   **Technical Implementation:** An `isDOMLocked` flag is set to `true` during `mousedown`.
*   **Violation Detection:** Any mutation detected by the `MutationObserver` while `isDOMLocked` is active results in an immediate **Freeze Violation (Score: 100)**, triggering an automatic block.

### C. Forensic Stack Analysis (`elementsFromPoint`)
When a click is initiated, the system performs a vertical scan of the DOM at the click coordinates.
*   **Identification:** It filters the stack for elements with `opacity < 0.1` and `pointer-events: auto`.
*   **Forensics:** Instead of just blocking, the system extracts the `id` or `class` of the transparent overlay to provide detailed security logs.

### D. Heuristic Scoring System
Clicks are evaluated based on a cumulative suspicion score:
*   **Behavioral Change (30-40 pts):** Rapid element changes under the cursor.
*   **Transparent Overlay (60 pts):** Detection of invisible layers.
*   **Freeze Violation (100 pts):** Programmatic changes attempted during the click interaction.

---

## 5. Components & Interface

### 🖥️ Real-time Security Monitor
Located at the bottom of the **Protected Page (`index.html`)**, this terminal-style UI mirrors internal security logs, suspicion scores, and mutation warnings for live transparency.

### 📊 Administrative Dashboard
*   **Live Activity Feed:** Real-time stream of all safe and blocked events.
*   **Threat Level Indicator:** Dynamically shifts from **SECURE** to **ALERT** based on recent attack frequency.
*   **Stats Tracking:** Visualizes protection rates, total clicks, and historical attack data.

### 🎯 Attack Simulator (`malicious.html`)
A controlled environment for testing four distinct attack vectors:
1.  **Button Swap:** Programmatic replacement of content.
2.  **Invisible Overlay:** Classic click-jacking layer.
3.  **Position Shift:** Moving the target away at the last moment.
4.  **Opacity Trick:** Rapid transparency toggling.

---

## 6. API Reference (Backend)
*   `POST /api/log-attack`: Logs a blocked event with target ID, malicious actor ID, and risk level.
*   `POST /api/log-click`: Records legitimate interactions to calculate protection accuracy.
*   `GET /api/get-stats`: Retrieves daily and all-time defense performance metrics.
*   `GET /api/get-recent-events`: Fetches the combined event stream for the dashboard.

---

## 7. Security Policy
This system is designed as a **Layer 2 Defense**. While it blocks browser-based manipulation, it is intended to complement standard security headers like `X-Frame-Options` and `Content-Security-Policy (CSP)`.
