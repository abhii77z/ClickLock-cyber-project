# ClickLock Simulation & Defense Guide

This guide details the **ClickLock** system, including implementation details for the four primary attack vectors and the defensive mechanisms used to neutralize them.

## 📁 File Structure
- `app.py`: Flask backend for serving pages and logging security events.
- `templates/test_console.html`: The primary testing interface containing simulation logic and the defender script.
- `templates/malicious.html`: Educational environment for visualizing attacks.
- `templates/defender_dashboard.html`: Live monitoring interface for security alerts.

## 🛠️ Dependencies
- **Backend**: Python 3.x, Flask
- **Frontend**: Modern Web Browser (Chrome/Edge/Firefox) with JavaScript enabled.
- **Tools**: No external JS libraries required (Vanilla JS implementation).

## 🚀 Execution Instructions
1.  **Start the Server**:
    Run `python app.py` from the project root.
2.  **Access Test Console**:
    Navigate to `http://localhost:5000/test-console` in your browser.
3.  **Simulate Attack**:
    Click any red **Attack Simulation** button (e.g., "Button Swap").
4.  **Execute Trigger**:
    Hover over or click the blue **Target Buttons** inside the dashed "Target Area".
5.  **Activate Defense**:
    Click the pink **Activate ClickLock** button and repeat the attack to observe the prevention mechanism.

---

## ⚔️ Attack Simulation Mechanisms

### 1. Button Swap
- **Method**: Utilizes a `mouseenter` event listener on the target button.
- **Logic**: The moment the user hovers over the button, the script changes the `textContent` and `style` to a malicious action (e.g., "Format Disk").
- **Goal**: Trick the user into confirming an action that changed visually just before the click.

### 2. Invisible Overlay
- **Method**: Dynamic DOM injection of a transparent overlay.
- **Logic**: Creates a transparent `<div>` (opacity ~0.01) positioned exactly over the target. It captures the `click` event directly.
- **Goal**: Hijack the click event so it never reaches the intended button.

### 3. Position Shift
- **Method**: CSS Transform manipulation on `mouseenter`.
- **Logic**: When the cursor enters the button area, the script applies a `transform` to move the button away instantly.
- **Goal**: Force the user to click a different location or a malicious element underneath.

### 4. Opacity Manipulation
- **Method**: Simultaneous opacity swapping on `mouseenter`.
- **Logic**: A hidden malicious button is placed exactly where the target button is. On hover, the target's opacity goes to `0`, and the malicious button's opacity goes to `1`.
- **Goal**: Swap the visible target with a malicious one during the hover/click sequence.

---

## 🛡️ How ClickLock Works

The ClickLock system uses a multi-layered approach to verify click integrity:

### 1. DOM Freezing (Mutation Observation)
- **Concept**: The system monitors all changes to the DOM.
- **Implementation**: A `MutationObserver` tracks attribute changes, text updates, and child removals **specifically within the Protected Target Area**.
- **Detection**: If any mutation occurs within **300ms** of a click event, it is flagged as a "Freeze Violation".

### 2. Cursor & Element Tracking
- **Concept**: Verifying what is actually under the cursor.
- **Implementation**: Uses `document.elementsFromPoint(x, y)` to retrieve a stack of all elements at the click coordinates.
- **Detection**: It checks the stack for elements with suspicious properties (e.g., `id="malicious-overlay"` or `id="opacity-trap"`).

### 3. Suspicion Scoring Engine
The system calculates a **Suspicion Score** (0-100) based on detected anomalies:
- **Invisible Overlay/Opacity Trap Detected**: +90 Score
- **DOM Mutation During Click (Freeze Violation)**: +100 Score

### 4. Event Blocking
If the Suspicion Score exceeds the threshold (**80**):
1.  `e.preventDefault()` is called to stop the default browser action.
2.  `e.stopImmediatePropagation()` prevents other scripts from receiving the click.
3.  The event is logged to the backend for analysis.
4.  A security alert is shown to the user.
