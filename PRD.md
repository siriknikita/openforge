# Product Requirements Document (PRD): OpenForge

## 1\. Introduction

### 1.1. Goal and Vision

The goal of **OpenForge** is to create a unified, real-time, AI-assisted platform that fundamentally redefines open-source collaboration. It aims to eliminate context switching, maximize developer flow (vibe-coding), and lower the barrier to entry for high-quality contributions by integrating all essential tools into a single, secure web-based "Room."

### 1.2. Target Audience

- **Primary:** Experienced Open-Source Contributors and Maintainers.
- **Secondary:** Developers new to a specific project (requiring fast onboarding).
- **User Job To Be Done (JTBD):** "Quickly and effectively integrate significant code-contribution into a complex open-source project, minimizing friction and receiving recognition from the community."

---

## 2\. Product Architecture and Technology Stack

| Component                | Technology                              | Rationale                                                                                                                                                                                                                                            |
| :----------------------- | :-------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Frontend**             | **React, Next.js, TailwindCSS, ShadCN** | **Next.js** provides excellent routing, server-side rendering (SSR) for performance, and API route capability. **React** for component-based UI. **TailwindCSS** and **ShadCN** (React components) for rapid, accessible, and modern UI development. |
| **Backend/API**          | **FastAPI** (Python)                    | High performance, asynchronous capabilities, and robust built-in data validation (Pydantic), which is ideal for handling real-time data streams and AI service integrations.                                                                         |
| **Database**             | **MongoDB**                             | Flexibility and scalability for handling dynamic data structures (user profiles, real-time session logs, project metadata).                                                                                                                          |
| **Database Driver**      | **PyMongo**                             | Official, robust driver for connecting the FastAPI backend to the MongoDB database.                                                                                                                                                                  |
| **Real-time/WebSockets** | _Backend Integration_                   | FastAPI provides robust WebSocket support necessary for the real-time editor and chat synchronization.                                                                                                                                               |
| **Code Editor**          | _Leverage existing library_             | Utilize a battle-tested library (e.g., Monaco Editor, the foundation of VS Code) for the in-browser IDE component.                                                                                                                                   |

---

## 3\. Functional Requirements (FR)

### 3.1. FR-1: Authentication and Onboarding

- **FR 1.1:** Users **must** be able to authenticate using their **GitHub account** (OAuth).
- **FR 1.2:** Upon first login, the user profile must be created by syncing basic information (username, avatar, email) from GitHub.
- **FR 1.3:** The platform must display a dashboard listing all projects the user is currently contributing to or maintaining.

### 3.2. FR-2: Project Management and Rooms

- **FR 2.1:** Every "Room" must be permanently **tied to a single GitHub repository**.
- **FR 2.2:** The platform must allow users to **create a new repository** (and thus a new Room) directly from the platform.
- **FR 2.3:** Each Room must display a summary page showing the project description, technology stack, documentation links, and current **open issues/tasks**.
- **FR 2.4:** The Room must contain the fully functional **in-browser IDE** (based on Monaco Editor) displaying the repository's code.

### 3.3. FR-3: Real-Time Vibe-Coding

- **FR 3.1:** Multiple users **must** be able to edit the same file simultaneously, with changes synchronized in **real-time** (similar to Google Docs or VS Code Live Share).
- **FR 3.2:** A real-time chat/communication panel must be available within the Room to facilitate coordination among human developers.
- **FR 3.3:** Users must be able to **create, manage, and close GitHub Issues** directly from the IDE interface without leaving the Room.

### 3.4. FR-4: AI Assistance and Vibe-Coding

- **FR 4.1:** The AI agent must be accessible via a dedicated panel/chat window in the IDE.
- **FR 4.2:** The AI must be able to **read the current file content, project context, and the developer's plan** (input by the user).
- **FR 4.3:** The core **Vibe-Coding** functionality is defined as: The AI **only implements code based on a detailed, user-provided plan** (e.g., pseudo-code, step-by-step instructions) to ensure architectural quality and user intent are met.
- **FR 4.4:** The AI must support the generation of tests, documentation, and refactoring suggestions.

---

## 4\. Non-Functional Requirements (NFR)

### 4.1. NFR-1: Performance

- **NFR 1.1:** Real-time latency for code synchronization **must be less than 100ms** to ensure a smooth "vibe-coding" experience.
- **NFR 1.2:** Initial Room load time (including code and editor) must be **less than 3 seconds**.

### 4.2. NFR-2: Security

- **NFR 2.1 (Secrets Management):** Environment variables/API keys for AI services (e.g., OpenAI, Gemini) **must only be visible and editable by the repository owner/trusted personnel**. These secrets must be stored securely (e.g., Vault or encrypted fields in MongoDB).
- **NFR 2.2 (Data Flow):** Secrets **must never be logged or printed** to any output or log file. They must be loaded directly into the backend process environment for use.
- **NFR 2.3 (AI Prompt Security):** All user prompts sent to the AI API **must pass through an internal API system prompt replacement** layer to inject security measures and evaluate the harmfulness of the prompt before execution.

### 4.3. NFR-3: Reputation and Metrics

- **NFR 3.1:** The platform must track individual developer metrics (number of issues solved, commits contributed, project evaluations).
- **NFR 3.2:** A basic **Reputation/Rank** indicator must be displayed on the developer's profile, calculated based on the metrics tracked in NFR 3.1.
