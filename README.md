---
title: OpenEnv Trust & Safety Analyst
emoji: 🕵️
colorFrom: blue
colorTo: red
sdk: docker
pinned: false
---

# PROBLEM STATEMENT
### Round 1 — Project Submission: OpenEnv: Trust & Safety Analyst

**THE TASK**
Build a complete, real-world OpenEnv environment where an AI agent acts as a corporate Trust & Safety Analyst. The agent must actively investigate user accounts by querying mock database logs and make high-stakes moderation decisions, learning through the standard `step()` / `reset()` / `state()` API.

**KEY REQUIREMENTS SATISFIED**
* **Real-world task:** Replicates the daily workflow of platform integrity and fraud investigation teams.
* **Full OpenEnv spec:** Strictly typed Pydantic models (`CaseObservation`, `AnalystAction`), `step()`/`reset()`/`state()` endpoints.
* **Baseline inference script:** Reproducible `inference.py` script outputting strict `[START]`, `[STEP]`, and `[END]` logs.
* **Hugging Face Space Deployment:** Containerized execution with a working `Dockerfile` exposing port 7860.