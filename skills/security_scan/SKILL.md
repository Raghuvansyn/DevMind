# Security Scanner Skill

## Purpose
Identify security vulnerabilities using OWASP Top 10 principles.
Each model request contains only its system prompt, this skill, and the current input.
The process keeps a scan counter and an in-memory request history. This is not a
security boundary or a substitute for validated static analysis and human review.

## Trigger conditions
- User asks about security, vulnerabilities, or scanning code

## Output format
RISK LEVEL → VULNERABILITY → DESCRIPTION → RECOMMENDATION with secure code example

## Skill version
1.0.0 — DevMind Capstone
