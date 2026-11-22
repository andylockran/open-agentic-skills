#!/usr/bin/env python3
"""
openspec-validate.py - OpenSpec Proposal and Contract Validator
Part of the 'andyapproach' skill. Author: andylockran

Validates that OpenSpec change proposals and interface contract declarations
comply with the mandatory Andy Approach governance standards.
"""

import sys
import re
from pathlib import Path

REQUIRED_PROPOSAL_SECTIONS = [
    "Problem Statement & Motivation",
    "Requirements (RFC 2119)",
    "Scope Boundaries",
    "Declared Interface Contracts",
    "Subagent Worktree Allocation",
    "Verification & Acceptance Criteria"
]

RFC_2119_KEYWORDS = ["MUST", "MUST NOT", "SHOULD", "SHOULD NOT", "MAY"]

def validate_proposal(filepath: Path) -> list:
    errors = []
    text = filepath.read_text(encoding="utf-8")

    # Check for required sections
    for sec in REQUIRED_PROPOSAL_SECTIONS:
        if not re.search(rf"^#+\s+.*{re.escape(sec)}", text, re.MULTILINE | re.IGNORECASE):
            errors.append(f"Missing required section: '{sec}'")

    # Check for RFC 2119 keywords in requirements
    found_rfc = any(kw in text for kw in RFC_2119_KEYWORDS)
    if not found_rfc:
        errors.append(f"Requirements section must include RFC 2119 keywords ({', '.join(RFC_2119_KEYWORDS)})")

    # Check for Out of Scope definition
    if "out of scope" not in text.lower():
        errors.append("Proposal must explicitly define an 'Out of Scope' boundary.")

    # Check for contract declaration reference
    if "openspec/contracts" not in text and ".openapi." not in text and "contract" not in text.lower():
        errors.append("Proposal must reference declared interface contracts in 'openspec/contracts/'.")

    # Check for worktree allocation reference
    if ".worktrees" not in text:
        errors.append("Proposal must declare an isolated subagent worktree allocation under '.worktrees/'.")

    return errors

def main():
    if len(sys.argv) < 2:
        print("Usage: openspec-validate.py <path-to-proposal.md>")
        sys.exit(1)

    target = Path(sys.argv[1])
    if not target.exists():
        print(f"Error: File not found: {target}")
        sys.exit(1)

    errors = validate_proposal(target)
    if errors:
        print(f"❌ Validation failed for {target.name}:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print(f"✅ OpenSpec proposal '{target.name}' passed all governance checks.")

if __name__ == "__main__":
    main()
