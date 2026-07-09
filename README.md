# ClickLock 🔒

A client-side security architecture designed to detect, analyze, and neutralize browser-based **Ghost Click (Clickjacking)** attacks.

---

## 💡 Why ClickLock is Used

Modern web applications are increasingly vulnerable to clickjacking attacks where malicious actors trick users into clicking invisible buttons or programmatic overlays. ClickLock addresses this gap through:

*   **Preventing Real-Time DOM Swaps (DOM Freezing)**: Malicious scripts often replace a safe button with a malicious link the millisecond a user initiates a mouse-down. ClickLock temporarily freezes mutations inside the protected zone during clicks, flagging and blocking any sudden changes.
*   **Neutralizing Transparent Overlays**: Attacks frequently use invisible layers (`opacity: 0.01` with `pointer-events: auto`) to intercept clicks meant for legitimate targets. ClickLock does structural coordinate stack analysis (`elementsFromPoint`) at runtime to expose transparent overlays.
*   **Security Forensics & Monitoring**: Standard browser protections rarely inform developers or users when clickjacking is blocked. ClickLock streams granular interaction telemetry (legitimate clicks vs. blocked attacks) to a Flask backend dashboard to provide visibility into attack attempts.

---

## 🔮 Future Scope

The roadmap for ClickLock centers on expanding coverage, increasing performance, and simplifying deployment:

*   **Machine Learning-Driven Behavioral Heuristics**: Implementing lightweight client-side models to analyze user cursor trajectories, acceleration patterns, and click timings to predict and classify robotic or forced interactions.
*   **Browser Extension Deployment**: Transitioning ClickLock from a per-page script to a unified browser extension that proactively monitors and immunizes all websites a user visits against transparent overlays.
*   **WebAssembly (WASM) Performance Core**: Rebuilding coordinate checking and stack forensic algorithms in WebAssembly to minimize runtime latency on high-frequency UI updates.
*   **Integrations with Enterprise SIEMs**: Enabling dashboard alerts and forensic reports to export logs directly into major SIEM environments (like Splunk or Datadog) for centralized corporate security operations.
*   **W3C/Browser Standardization Proposing**: Proposing the temporal DOM freeze lock API to standard groups as a native browser security header (like CSP or X-Frame-Options) to run directly inside the browser engine.