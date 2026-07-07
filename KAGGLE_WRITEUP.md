# 🧠 DevMind — Kaggle AI Agents Intensive Capstone 2025

## Submission Overview

**Project:** DevMind — Multi-Agent AI Developer Assistant  
**Author:** [Raghuvansyn](https://github.com/Raghuvansyn)  
**Repository:** [github.com/Raghuvansyn/DevMind](https://github.com/Raghuvansyn/DevMind)  
**Demo Video:** [YouTube](https://youtu.be/r1_tX-W0pPw)  
**Competition:** [Kaggle AI Agents Intensive Capstone 2025](https://www.kaggle.com/competitions/ai-agents-intensive-capstone-2025)

---

## Problem Statement

Developers constantly context-switch between tools for different tasks — one tool for code review, another for security analysis, yet another for documentation. This fragmentation reduces productivity and increases cognitive load.

**DevMind** solves this by providing a unified, intelligent interface that automatically understands what the developer needs and routes the request to the best-suited AI specialist.

---

## Solution Architecture

DevMind implements a **multi-agent orchestration pattern** with the following components:

### Orchestrator
- Receives natural language input from the developer
- Runs a **security guard** (regex-based filtering) to block dangerous patterns
- Performs **intent classification** using keyword matching
- Dispatches the request to the appropriate specialist agent

### Specialist Agents

| Agent | Role | System Prompt Focus |
|---|---|---|
| **Code Analyst** | Reviews code for bugs, performance issues, and anti-patterns | Issue → Explanation → Fix with before/after code |
| **Security Scanner** | Identifies OWASP Top 10 vulnerabilities | Risk Level → Vulnerability → Description → Recommendation |
| **Doc Writer** | Generates documentation, docstrings, and READMEs | Google-style docstrings, structured README format |

### MCP Server (Model Context Protocol)
- Serves as a **tool layer** providing progressive skill disclosure
- Each agent has a corresponding `SKILL.md` file defining its capabilities
- Skill context is loaded on-demand and injected into the agent's system prompt
- Also provides secure file reading with extension whitelisting and path traversal protection

### LLM Backend
- **Model:** Llama 3.3 70B via Groq API
- **Temperature:** 0.3 (focused, deterministic responses)
- **Max Tokens:** 1024

---

## Key Concepts Demonstrated

### 1. Multi-Agent Orchestration
The system uses a central orchestrator that manages multiple specialized agents, each with distinct capabilities and system prompts.

### 2. Intent Classification & Task Routing
Natural language input is classified into categories and routed to the most appropriate agent without requiring the user to manually select one.

### 3. Progressive Disclosure via SKILL.md
Agents receive domain-specific context through SKILL.md files served by the MCP server. This keeps base prompts lean while allowing rich, specialized behavior when needed.

### 4. Security Guardrails
Input is filtered through regex patterns that detect and block potentially dangerous commands (`rm -rf`, `eval()`, `exec()`, `os.system()`, etc.).

### 5. Audit Logging
Every interaction is logged with agent attribution, enabling full traceability of the system's routing decisions.

### 6. Zero-Trust Design
The security scanner agent operates with ephemeral context — no state is persisted between scans, following zero-trust principles.

---

## Technical Implementation

### File Structure

```
DevMind/
├── orchestrator.py        # Main orchestrator + routing + security guard
├── agents/
│   ├── base_agent.py      # Base class with Groq API integration
│   ├── code_analyst.py    # Code review specialist
│   ├── security_scan.py   # Security vulnerability scanner
│   └── doc_writer.py      # Documentation generator
├── skills/
│   ├── code_analyst/SKILL.md
│   ├── security_scan/SKILL.md
│   └── doc_writer/SKILL.md
├── mcp/
│   └── mcp_server.py      # MCP server for skill context
└── requirements.txt
```

### Dependencies
- `requests>=2.31.0` — HTTP client for Groq API
- `python-dotenv>=1.0.0` — Environment variable management

---

## What I Learned

1. **Agent specialization** produces better results than a single general-purpose agent
2. **Progressive disclosure** through SKILL.md files is an effective way to manage prompt complexity
3. **Security-first design** is essential when building AI systems that process arbitrary user input
4. **MCP (Model Context Protocol)** provides a clean abstraction for tool and context management
5. **Groq's inference speed** makes interactive multi-agent systems practical for real-time use

---

## Future Directions

- Web dashboard for real-time agent visualization
- GitHub integration for automated PR reviews
- Memory and RAG for context-aware multi-turn conversations
- Additional specialist agents (testing, deployment, refactoring)
- Docker and cloud deployment

---

## Acknowledgments

- **Kaggle** for the AI Agents Intensive program
- **Groq** for fast LLM inference
- **Meta** for the Llama 3.3 70B model
