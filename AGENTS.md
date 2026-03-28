# TrialPulse Agent Specification (AGENTS.md)

This document outlines the operational guidelines, architectural rules, and best practices that all AI coding agents must follow when contributing to the TrialPulse repository.

## 1. Project Context & Role
- **Role:** You are an AI coding agent contributing to TrialPulse, a clinical trial patient safety and engagement platform.
- **Structure:** The application is a monorepo consisting of:
  - **Backend:** A fully asynchronous Python FastAPI monolith.
  - **Frontend (Web):** A React 18 + TypeScript web dashboard for researchers.
  - **Mobile App:** A React Native (Expo) app for patients.
- **Goal:** Maintain clean, async, event-driven, and highly observable code suitable for a healthcare prototype.

## 2. Git Workflow & Source Control

All agents must adhere to a strict branching and commit workflow to ensure code quality and traceability.

### 2.1 Branching Strategy
- **Never Push to Main:** Direct pushes to the `main` branch are strictly prohibited. All changes must go through a Pull Request.
- **Branch Naming:** Branch names MUST use a `type/description` format.
  - *Examples:* `feat/voice-checkin-ui`, `fix/anomaly-detection-math`, `refactor/alert-engine`, `docs/api-specs`

### 2.2 Commit Guidelines
- **Conventional Commits:** You must strictly follow the [Conventional Commits](https://www.conventionalcommits.org/) format for all commit subjects.
  - *Examples:* `feat(backend): implement point anomaly detection for wearables`, `fix(mobile): resolve quick reply rendering issue`
- **Commit Bodies (Mandatory):** Every commit MUST include a descriptive subject line AND a detailed, multiline commit description.
  - The body should explain the *why* and *how* of the change, not just the *what*.
  - If a commit contains multiple logical changes or touches several components, use bullet points in the description body to detail each change.
- **Pull Requests:** Always open Pull Requests for review. PR descriptions must accurately summarize the changes and link to any relevant issue tracking numbers.

## 3. Mandatory Detailed Logging

Detailed, structured logging is a project-wide requirement. Visibility into event flows, AI state, and asynchronous tasks is critical.

- **Action Tracking:** Every significant action, state change (e.g., LangGraph node transitions), or external API call MUST be logged.
- **Structured Logging:** Use the configured structured Python logger (e.g., standard `logging` with JSON formatting or `loguru`).
- **Log Levels:** Use `INFO` for lifecycle events/requests, `WARNING` for recoverable issues/retries, `ERROR` for exceptions, and `DEBUG` for verbose AI/API traces.
- **Prohibition on Print Output:** Do not use `print()` or `console.log()` for operational logging. These are strictly for temporary local debugging and must be removed before committing.
- **Contextual Logs:** Include relevant context (e.g., `patient_id`, `session_id`, `trial_id`, `event_type`) in log events to facilitate debugging.

## 4. Architectural Rules & Best Practices

### 4.1 Backend (Python / FastAPI)
- **Async First:** The entire backend is built on `asyncio`. Use `await` for database calls, Redis pub/sub, external requests, and LLM generation. Do not block the event loop with synchronous operations.
- **Event-Driven Communication:** Modules must not tightly couple their business logic. Instead, publish events to the Redis event bus (`app/events/bus.py`).
  - *Example:* The `checkin` module shouldn't call the `alert` module directly. It publishes `symptom.reported`, which the alert engine listens to.
- **Database Access:** Use the async `SQLAlchemy` ORM and `asyncpg`. Avoid raw SQL strings unless optimizing a complex analytics query. Use UUIDs for IDs and `TIMESTAMPTZ` for timestamps.
- **Dependency Injection:** Heavily utilize FastAPI's `Depends()` for database sessions, Redis clients, and current user extraction.
- **LLM Abstraction:** NEVER hardcode Anthropic or OpenAI API calls. All LLM calls must go through the vendor-agnostic LangChain/LangGraph abstraction (`app/ai/llm.py`).

### 4.2 Frontend (Web Dashboard) & Mobile (React Native)
- **State Management:** Use `React Query` for all server-state (fetching, caching, background refetching, mutations). Use `Zustand` only for local, lightweight UI state.
- **Styling:** Use `Tailwind CSS` for web and `NativeWind` for mobile. Keep styling logic utility-first and avoid custom CSS files.
- **Type Safety:** Ensure strict TypeScript typing for all API responses, component props, and state slices. Avoid `any`.
- **Real-time Updates:** Use the native FastAPI WebSockets for dashboard live updates. Handle connection drops and reconnects gracefully.

## 5. Security & Environment Configuration
- **Mock Data First:** As this is a hackathon prototype, do not write code that connects to real external patient data streams unless explicitly requested. Rely on the `seed.sql` and data generation scripts.
- **Secrets Management:** Never hardcode API keys or database passwords. Always rely on the `Pydantic Settings` object in `app/config.py` to load from environment variables.

## 6. Testing Strategy
- Ensure coverage for critical paths: the symptom check-in flow, anomaly detection math, and alert engine rules.
- For backend updates, use `pytest` with `pytest-asyncio`.
- Mock external dependencies (like LiveKit or external LLMs) when writing unit tests to keep CI fast.
