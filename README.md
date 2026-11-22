# open-agentic-skills
A collection of useful agentic skills that I'd encourage anyone to use.

## Available Skills

### [andyapproach](./skills/andyapproach/SKILL.md)
Mandatory engineering workflow governance for AI-assisted development:
- **Spec-First**: Enforces formal change proposals via OpenSpec before implementation.
- **Contract-First**: Declares and freezes machine-verifiable interface contracts (OpenAPI, JSON Schema, Protobuf, TypeScript types) before spawning child subagents.
- **Worktree Isolation**: Forces subagents to collaborate on a single host Git repository exclusively via isolated `git worktree` checkouts.

### [govuk-digital-standards](./skills/govuk-digital-standards/SKILL.md)
Compliance, architecture, and audit framework for UK Public Sector digital delivery:
- **GDS Service Standard**: Comprehensive 14-point service delivery guide (user research, plain English, GOV.UK Design System, accessibility, open source, and 4 mandatory KPIs).
- **Technology Code of Practice (TCoP)**: 10 criteria governing cloud-first architecture, open standards & APIs (RFC 7807, OpenAPI 3.0+), data protection, and anti-lock-in.
- **NCSC Secure by Design (SbD)**: 8 core cybersecurity principles covering STRIDE threat modeling, zero-trust layered defense, encryption in transit/rest, and automated CI security gates (SAST, secret scanning, SCA).
- **Automated Audit CLI**: Includes [`audit-govuk-standards.py`](./skills/govuk-digital-standards/scripts/audit-govuk-standards.py) for evaluating repository readiness and generating RAG scorecards.


