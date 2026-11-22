# OpenSpec Proposal: [Feature Title]

- **Proposal ID**: PROP-[NUMBER]
- **Date**: YYYY-MM-DD
- **Author**: andylockran (or Subagent ID)
- **Status**: Draft
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
- **Out of Scope**:
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
