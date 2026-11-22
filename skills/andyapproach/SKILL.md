---
name: andyapproach
description: Mandatory engineering workflow governance for AI-assisted development. Enforces Git worktree isolation for multi-agent collaboration, requires OpenSpec change proposals before implementation, and mandates explicit interface declarations before spawning child subagents.
license: Apache-2.0
metadata:
  author: andylockran
---

> **Author**: andylockran  
> **License**: Apache-2.0 (Attribution Required)

# The Andy Approach (`andyapproach`)

The **Andy Approach** is the architectural and operational standard for developing applications with autonomous AI agents and subagents. It prevents the most common failure modes in multi-agent software engineering: working-tree clobbering, specification drift, ambiguous requirements, and uncoordinated code generation.

---

## 🏛️ The Three Inviolable Laws

```text
               ┌────────────────────────────────────────────────────────┐
               │              LAW 1: SPEC-FIRST (OpenSpec)              │
               │  No code is written without an approved OpenSpec RFC.  │
               └───────────────────────────┬────────────────────────────┘
                                           │
                                           ▼
               ┌────────────────────────────────────────────────────────┐
               │           LAW 2: CONTRACT-FIRST INTERFACES             │
               │  Declare and freeze interfaces BEFORE spawning workers.│
               └───────────────────────────┬────────────────────────────┘
                                           │
                                           ▼
               ┌────────────────────────────────────────────────────────┐
               │           LAW 3: GIT WORKTREE ISOLATION                │
               │ Subagents collaborate exclusively in dedicated trees.  │
               └────────────────────────────────────────────────────────┘
```

1. **Law 1: Spec-First via OpenSpec (No Spec, No Code)**  
   No agent or developer may create, modify, or refactor application code without an approved change proposal structured in the **OpenSpec** format under `openspec/proposals/`. The specification defines context, requirements (RFC 2119), scope boundaries, and verification criteria.

2. **Law 2: Contract-First Architecture (Declare Interfaces Before Spawning)**  
   Before any subagent, worker, or child process is spawned to implement a component, the orchestrating agent **MUST** define, commit, and freeze explicit, machine-verifiable interface declarations (OpenAPI, JSON Schema, Protobuf, TypeScript/Pydantic types, or CLI contracts) in `openspec/contracts/`. Child processes are given exact contract definitions, never vague textual goals.

3. **Law 3: Git Worktree Isolation (Zero Working-Tree Contamination)**  
   All subagents collaborate on a single host Git repository exclusively through **Git Worktrees** (`git worktree add`). Subagents **MUST NEVER** make changes directly in the main working tree or share an unstaged working directory. Each subagent operates within its own dedicated worktree directory, executing tests and commits in isolation before merging.

---

## 📁 Repository Directory Standard

Any application governed by the Andy Approach must maintain the following structure:

```text
<repository-root>/
├── openspec/                          # OpenSpec governance and contracts
│   ├── specs/                         # Base system domain specifications
│   │   ├── auth.md
│   │   └── data-pipeline.md
│   ├── proposals/                     # Active change proposals / RFCs
│   │   ├── 2026-11-22-oauth-pkce.md
│   │   └── 2026-11-23-event-broker.md
│   └── contracts/                     # Machine-verifiable interface contracts
│       ├── auth-api.openapi.yaml      # OpenAPI 3.1 REST schema
│       ├── event-schema.json          # JSON Schema event payload
│       └── types.ts                   # Strict type definitions / interfaces
├── .worktrees/                        # Ephemeral Git worktrees for subagents (gitignored)
│   ├── feat-oauth-pkce/               # Worktree for subagent A
│   └── feat-event-broker/             # Worktree for subagent B
├── .gitignore                         # MUST include /.worktrees/
└── src/                               # Application source code
```

---

## 🔄 End-to-End Execution Lifecycle

### Phase 1: Propose Changes via OpenSpec

Before any code editing tool is called:
1. Create a new change proposal file in `openspec/proposals/YYYY-MM-DD-<feature-slug>.md` using the [OpenSpec Proposal Template](#openspec-proposal-template).
2. The proposal **MUST** include:
   - **Context & Motivation**: Why this change is necessary.
   - **Specification Requirements**: Functional and non-functional requirements using standard RFC 2119 keywords (`MUST`, `MUST NOT`, `SHOULD`, `MAY`).
   - **Boundary Definition**: Explicit list of what is strictly **OUT OF SCOPE**.
   - **Interface Deltas**: Description of additions or modifications to public APIs or internal contracts.
   - **Verification Strategy**: Automated test scenarios, edge cases, and performance criteria.
3. Review and validate the proposal using `python3 scripts/openspec-validate.py openspec/proposals/<proposal>.md`.
4. Commit the approved proposal to the integration branch.

---

### Phase 2: Declare Interfaces & Contracts

Before delegating work to any child subagent or child process:
1. Create or update the formal contract files in `openspec/contracts/`:
   - **HTTP/REST APIs**: OpenAPI 3.1 specification (`.yaml` or `.json`).
   - **gRPC / RPC**: Protocol Buffer files (`.proto`).
   - **Event Streams / Messages**: JSON Schema or Avro schemas.
   - **Internal Modules / Packages**: TypeScript `.d.ts` / `types.ts`, Python `typing` protocols / Pydantic models, Rust traits, or Go interfaces.
2. Produce a **Contract Verification Fixture / Mock**:
   - Provide an executable test fixture or schema validation test (e.g. `tests/contracts/test_auth_api.py` or `contracts/auth.spec.ts`) that asserts compliance with the interface.
3. Commit the contract and test fixture to the baseline branch so all worktrees inherit it.

---

### Phase 3: Provision Isolated Git Worktree

Subagents must never run in the root working directory where concurrent edits or uncommitted files could be overwritten.

1. Create a dedicated worktree for the subagent:
   ```bash
   # Syntax: git worktree add -b <branch-name> .worktrees/<worktree-name> <base-branch>
   git worktree add -b feat/oauth-pkce .worktrees/feat-oauth-pkce main
   ```
2. Verify `.worktrees/` is present in `.gitignore`:
   ```bash
   grep -qxF "/.worktrees/" .gitignore || echo "/.worktrees/" >> .gitignore
   ```
3. Initialize dependencies inside the worktree if required by the language tooling (e.g. `npm install`, `uv sync`, or `cargo check`).

---

### Phase 4: Spawn Subagent with Explicit Context

When invoking a subagent (via `invoke_subagent` or a child background task), the prompt **MUST** explicitly specify:
1. **Worktree Path**: The absolute path to the dedicated worktree directory (e.g. `/path/to/repo/.worktrees/feat-oauth-pkce`).
2. **Contract Path**: The exact path to the frozen interface contract in `openspec/contracts/`.
3. **Verification Command**: The exact test command that proves compliance with the contract.

#### Subagent Dispatch Example:
```text
Task: Implement OAuth2 PKCE login provider according to the OpenSpec proposal.
Working Directory (Git Worktree): /home/user/app/.worktrees/feat-oauth-pkce
Declared Contract: /home/user/app/openspec/contracts/auth-api.openapi.yaml
Contract Test Suite: pytest tests/contracts/test_oauth_pkce.py

Guidelines:
1. You MUST execute all commands and file operations within your assigned worktree.
2. Do NOT modify files outside the worktree.
3. Implement the feature so that it strictly adheres to the OpenAPI contract.
4. Run the contract verification suite until all tests pass with 100% compliance.
5. Create atomic, conventional commits on branch 'feat/oauth-pkce'.
```

---

### Phase 5: Verification, Merge, and Worktree Pruning

Once the subagent signals completion:
1. **Contract Verification**:
   The parent coordinator runs the contract verification and integration tests within the worktree:
   ```bash
   cd .worktrees/feat-oauth-pkce && pytest tests/contracts/
   ```
2. **Reconciliation / Rebase**:
   Ensure the feature branch is cleanly rebased on the latest integration branch:
   ```bash
   git -C .worktrees/feat-oauth-pkce fetch origin
   git -C .worktrees/feat-oauth-pkce rebase origin/main
   ```
3. **Merge**:
   Merge the validated branch into the target branch:
   ```bash
   git checkout main
   git merge --ff-only feat/oauth-pkce || git merge --squash feat/oauth-pkce
   ```
4. **Worktree Cleanup**:
   Remove the worktree and prune the Git administrative metadata:
   ```bash
   git worktree remove --force .worktrees/feat-oauth-pkce
   git worktree prune
   git branch -d feat/oauth-pkce
   ```

---

## 📝 OpenSpec Proposal Template

Save proposals in `openspec/proposals/YYYY-MM-DD-<slug>.md`:

```markdown
# OpenSpec Proposal: [Feature Title]

- **Proposal ID**: PROP-[NUMBER]
- **Date**: YYYY-MM-DD
- **Author**: andylockran (or Agent ID)
- **Status**: [Draft | In Review | Approved | Implemented | Superseded]
- **Target Branch**: main

## 1. Problem Statement & Motivation
Describe the context, user pain point, or technical debt being addressed. Why is this necessary?

## 2. Requirements (RFC 2119)
- **REQ-1**: The system MUST [mandatory requirement].
- **REQ-2**: The component MUST NOT [prohibited behavior].
- **REQ-3**: The service SHOULD [recommended optimization].
- **REQ-4**: The API MAY [optional capability].

## 3. Scope Boundaries
- **In Scope**:
  - [Explicitly supported item]
- **Out of Scope (Forbidden for this change)**:
  - [Explicitly deferred or excluded item]

## 4. Declared Interface Contracts
List all interfaces that must be declared before spawning subagents:
- Contract file: `openspec/contracts/[contract-file.yaml]`
- Type definitions: `openspec/contracts/[types.ts]`
- Verification test: `tests/contracts/[test_contract.py]`

## 5. Subagent Worktree Allocation
- **Worktree Name**: `.worktrees/feat-[slug]`
- **Feature Branch**: `feat/[slug]`
- **Assigned Subagent Role**: [e.g. Backend API Builder]

## 6. Verification & Acceptance Criteria
- [ ] Contract validation tests pass.
- [ ] Unit and integration test coverage meets threshold (>= 80%).
- [ ] No regression on existing test suite.
- [ ] Worktree cleanly removed after merge.
```

---

## 🛠️ Worktree Helper Commands Reference

Use the bundled `worktree-manager.sh` script or native Git commands:

```bash
# List all active worktrees and branches
git worktree list

# Create a new isolated worktree on a new branch
git worktree add -b feat/<name> .worktrees/<name> main

# Lock a worktree to prevent accidental pruning during long tasks
git worktree lock .worktrees/<name> --reason "Subagent currently compiling"

# Unlock after subagent completion
git worktree unlock .worktrees/<name>

# Remove a completed worktree safely
git worktree remove .worktrees/<name>

# Prune stale worktree references from .git/worktrees
git worktree prune
```

---

## ⚠️ Anti-Patterns & Prohibitions

| Anti-Pattern | Why It Fails | The Andy Approach Way |
| :--- | :--- | :--- |
| **Direct Root Editing** | Multiple agents modify the main repo working tree, causing merge conflicts and race conditions. | Every subagent works in a dedicated `.worktrees/<name>` directory. |
| **Vague Prompting** | Telling subagents "build user auth" results in hallucinations, mismatched schemas, and broken APIs. | The parent declares the OpenAPI / TypeScript contract before spawning the worker. |
| **Spec-Free Coding** | Jumping straight to code produces features that drift from architectural requirements. | Every change begins with an approved OpenSpec RFC proposal. |
| **Orphaned Worktrees** | Leaving worktrees around pollutes disk space and locks branches from being rebased. | Worktrees are strictly ephemeral: merge, remove, and prune immediately upon verification. |
| **Shared Working Trees** | Pointing two subagents to the same worktree directory creates race conditions. | One worktree per subagent. Always. |
