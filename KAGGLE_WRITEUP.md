# DevMind implementation notes

This repository describes DevMind as a project for the [Kaggle AI Agents Intensive Capstone 2025](https://www.kaggle.com/competitions/ai-agents-intensive-capstone-2025). The repository history attributes the original implementation to [Ankit Singh Raghuvanshi](https://github.com/Raghuvansyn). Participation, submission, and competition results have not been independently verified from the repository.

The [previously recorded video link](https://youtu.be/-DHTtXIJ8g8) is preserved; its contents and availability were not verified during the code review.

## Problem and implementation

DevMind offers one Python CLI for requesting code reviews, documentation drafts, and potential security findings. Its orchestrator applies validation and a regex input filter, chooses one specialist using keyword rules, loads that specialist's `SKILL.md`, and makes one Groq chat completion request.

The three specialists share the same `BaseAgent` HTTP implementation and model; their roles differ through system prompts and skill context. They do not collaborate on a request or autonomously execute tools. Specialization is a design choice, and no comparative evaluation establishes that it outperforms a single prompt.

The local helper named `MCPServer` caches skill files and offers a workspace-contained file reader. It is ordinary Python code with no Model Context Protocol transport, protocol methods, or external MCP client integration. The CLI does not read a file merely because its path appears in input.

## Model and state

The configured model is `llama-3.3-70b-versatile` via Groq, with temperature `0.3`, a maximum of `1024` output tokens, and a `30` second HTTP timeout. Model access depends on provider availability and an API key.

Every model call contains the current input and system/skill instructions. Previous conversation messages are not sent. The process retains a security scan counter and an in-memory request history, so describing the entire application as stateless or as a zero-trust system would be inaccurate.

## Validation and evidence

The offline suite verifies request construction, skill injection, routing, file containment, blocked requests, missing keys, and provider failure handling. Twelve hand-authored routing examples are regression cases, not a representative accuracy benchmark. The offline demonstration replaces the provider HTTP response with a clearly labeled fixture.

No live model quality, security detection accuracy, latency, cost, scalability, or production readiness result is established by these checks. Follow the [README](README.md) for reproducible setup, commands, local verification details, and remaining limitations.

## Future directions

Priorities are an explicit route selector, an independent review-quality evaluation with human labels, and structured findings validation. Real MCP integration, retrieval, GitHub integration, persistent memory, a web interface, and deployment remain future work.

## Acknowledgments

- Kaggle for the AI Agents Intensive program.
- Groq for the inference API.
- Meta for the Llama model.

The existing MIT license and copyright notice are unchanged.
