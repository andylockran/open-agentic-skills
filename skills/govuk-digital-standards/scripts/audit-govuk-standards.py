#!/usr/bin/env python3
"""audit-govuk-standards.py

Automated compliance auditor for the UK Public Sector Digital Standards triad:
1. GDS Service Standard (14 points)
2. CDDO Technology Code of Practice (TCoP - 10 criteria)
3. NCSC Secure by Design (SbD - 8 principles)

Usage:
    python3 audit-govuk-standards.py [--target <path>] [--format {text|json|markdown}]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class CheckResult:
    id: str
    pillar: str  # "GDS", "TCoP", "SbD"
    criterion: str
    title: str
    status: str  # "PASS", "WARN", "FAIL"
    details: str
    remediation: Optional[str] = None


class GovUKStandardsAuditor:
    def __init__(self, root_dir: Path):
        self.root = root_dir.resolve()
        self.results: List[CheckResult] = []

    def run_all(self) -> List[CheckResult]:
        self.results = []
        self._check_open_source_licensing()
        self._check_accessibility_tooling()
        self._check_govuk_design_system()
        self._check_secret_scanning_and_security_ci()
        self._check_open_api_standards()
        self._check_privacy_and_security_docs()
        self._check_cloud_native_configuration()
        self._check_secure_by_design_controls()
        return self.results

    def _has_file_matching(self, patterns: List[str]) -> bool:
        for pat in patterns:
            if list(self.root.glob(pat)):
                return True
        return False

    def _search_file_content(self, patterns: List[str], regex: str) -> bool:
        rgx = re.compile(regex, re.IGNORECASE)
        for pat in patterns:
            for filepath in self.root.glob(pat):
                if filepath.is_file():
                    try:
                        content = filepath.read_text(encoding="utf-8", errors="ignore")
                        if rgx.search(content):
                            return True
                    except Exception:
                        continue
        return False

    # 1. GDS Point 12 / TCoP Point 3: Open Source by Default
    def _check_open_source_licensing(self) -> None:
        has_license = any((self.root / name).exists() for name in ["LICENSE", "LICENSE.md", "LICENCE", "LICENCE.md"])
        if has_license:
            self.results.append(
                CheckResult(
                    id="GDS-12-OPEN-SOURCE",
                    pillar="GDS",
                    criterion="Point 12 (Make new source code open) & TCoP Point 3",
                    title="Open Source Licensing (Code in the open)",
                    status="PASS",
                    details="Repository declares an explicit public open-source license file.",
                )
            )
        else:
            self.results.append(
                CheckResult(
                    id="GDS-12-OPEN-SOURCE",
                    pillar="GDS",
                    criterion="Point 12 (Make new source code open) & TCoP Point 3",
                    title="Open Source Licensing (Code in the open)",
                    status="FAIL",
                    details="No LICENSE or LICENCE file found in root.",
                    remediation="Add an approved open source license (e.g. MIT, Apache-2.0, Open Government Licence) to fulfill GDS Point 12 and TCoP Point 3.",
                )
            )

    # 2. GDS Point 5 / TCoP Point 2: Accessibility
    def _check_accessibility_tooling(self) -> None:
        a11y_markers = [
            "axe-core",
            "@axe-core",
            "pa11y",
            "eslint-plugin-jsx-a11y",
            "cypress-axe",
            "playwright.*axe",
            "jest-axe",
            "html-validate",
        ]
        has_a11y_deps = self._search_file_content(
            ["package.json", "package-lock.json", "pyproject.toml", "requirements*.txt", ".github/workflows/*.y*ml"],
            "|".join(a11y_markers),
        )
        has_a11y_doc = any(
            (self.root / name).exists()
            for name in [
                "ACCESSIBILITY.md",
                "docs/accessibility.md",
                "accessibility-statement.md",
                "docs/accessibility-statement.md",
            ]
        )

        if has_a11y_deps and has_a11y_doc:
            status = "PASS"
            details = "Automated accessibility testing tools and Accessibility Statement documentation detected."
            remediation = None
        elif has_a11y_deps or has_a11y_doc:
            status = "WARN"
            details = f"Partial accessibility coverage (Tooling: {has_a11y_deps}, Statement doc: {has_a11y_doc})."
            remediation = "Ensure both automated accessibility testing (axe-core/pa11y for WCAG 2.2 AA) and a published ACCESSIBILITY.md statement exist."
        else:
            status = "FAIL"
            details = "No automated accessibility linting/testing or accessibility statement found."
            remediation = "Integrate axe-core or pa11y into CI and publish an accessibility statement complying with WCAG 2.2 Level AA.",
        
        self.results.append(
            CheckResult(
                id="GDS-05-ACCESSIBILITY",
                pillar="GDS",
                criterion="Point 5 (Make sure everyone can use the service) & TCoP Point 2",
                title="Accessibility & WCAG 2.2 AA Assurance",
                status=status,
                details=details,
                remediation=remediation if isinstance(remediation, str) else remediation[0] if remediation else None,
            )
        )

    # 3. GDS Point 4 & Point 13: GOV.UK Design System & Common Platforms
    def _check_govuk_design_system(self) -> None:
        govuk_markers = [
            "govuk-frontend",
            "govuk-react",
            "govuk_template",
            "@govuk-one-login",
            "govuk-notify",
            "notifications-node-client",
            "notifications-python-client",
            "govuk-pay",
        ]
        has_govuk_assets = self._search_file_content(
            ["package.json", "pyproject.toml", "Gemfile", "requirements*.txt", "src/**/*.html", "templates/**/*.html", "app/**/*.html"],
            "|".join(govuk_markers),
        )
        if has_govuk_assets:
            self.results.append(
                CheckResult(
                    id="GDS-13-COMMON-PLATFORMS",
                    pillar="GDS",
                    criterion="Point 4 (Make simple to use) & Point 13 (Use open standards and common platforms)",
                    title="GOV.UK Design System & Common Platforms Adoption",
                    status="PASS",
                    details="References to GOV.UK Frontend, One Login, Notify, or Pay detected.",
                )
            )
        else:
            self.results.append(
                CheckResult(
                    id="GDS-13-COMMON-PLATFORMS",
                    pillar="GDS",
                    criterion="Point 4 (Make simple to use) & Point 13 (Use open standards and common platforms)",
                    title="GOV.UK Design System & Common Platforms Adoption",
                    status="WARN",
                    details="No direct references to GOV.UK Frontend, One Login, Notify, or Pay detected in dependencies.",
                    remediation="If building public-facing web interfaces, adopt govuk-frontend and common platforms (Notify, Pay, One Login) to maintain consistency.",
                )
            )

    # 4. TCoP Point 6 & SbD Principle 7: Secret Scanning & CI Security
    def _check_secret_scanning_and_security_ci(self) -> None:
        sec_markers = [
            "gitleaks",
            "trufflehog",
            "semgrep",
            "codeql",
            "snyk",
            "trivy",
            "dependabot",
            "renovate",
            "bandit",
            "safety",
            "npm audit",
        ]
        has_sec_ci = self._search_file_content(
            [".github/workflows/*.y*ml", ".gitlab-ci.yml", "azure-pipelines.yml"],
            "|".join(sec_markers),
        )
        if has_sec_ci:
            self.results.append(
                CheckResult(
                    id="SBD-07-CONTINUOUS-SECURITY",
                    pillar="SbD",
                    criterion="SbD Principle 7 & TCoP Point 6 (Make things secure)",
                    title="Continuous Security & Secret Scanning in CI",
                    status="PASS",
                    details="Automated security scanning (SAST, secret scanning, or SCA) detected in CI workflows.",
                )
            )
        else:
            self.results.append(
                CheckResult(
                    id="SBD-07-CONTINUOUS-SECURITY",
                    pillar="SbD",
                    criterion="SbD Principle 7 & TCoP Point 6 (Make things secure)",
                    title="Continuous Security & Secret Scanning in CI",
                    status="FAIL",
                    details="No automated secret scanning, SAST, or dependency vulnerability checks found in CI workflows.",
                    remediation="Add automated secret scanning (gitleaks/trufflehog) and SAST/SCA (CodeQL, Semgrep, Trivy) to CI pipelines.",
                )
            )

    # 5. TCoP Point 4: Open Standards & APIs
    def _check_open_api_standards(self) -> None:
        has_openapi = (
            self._has_file_matching(["openapi.y*ml", "openapi.json", "swagger.y*ml", "swagger.json", "docs/api/openapi.y*ml"])
            or self._search_file_content(["package.json", "pyproject.toml"], "fastapi|swagger|openapi|tsoa")
        )
        if has_openapi:
            self.results.append(
                CheckResult(
                    id="TCOP-04-OPEN-STANDARDS",
                    pillar="TCoP",
                    criterion="TCoP Point 4 (Make use of open standards)",
                    title="Open API & Standard Data Formats",
                    status="PASS",
                    details="OpenAPI / Swagger specifications or framework generators identified.",
                )
            )
        else:
            self.results.append(
                CheckResult(
                    id="TCOP-04-OPEN-STANDARDS",
                    pillar="TCoP",
                    criterion="TCoP Point 4 (Make use of open standards)",
                    title="Open API & Standard Data Formats",
                    status="WARN",
                    details="No OpenAPI/REST standard contracts detected.",
                    remediation="Publish machine-readable OpenAPI specifications (OAS 3.0+) and follow Central Digital and Data Office API technical standards.",
                )
            )

    # 6. GDS Point 9 & SbD Principle 1: Threat Modeling & Privacy Documentation
    def _check_privacy_and_security_docs(self) -> None:
        has_threat_model = self._has_file_matching(
            ["SECURITY.md", "THREAT_MODEL.md", "docs/threat-model.md", "docs/security.md", "docs/dpia.md"]
        )
        has_security_md = (self.root / "SECURITY.md").exists()

        if has_security_md and has_threat_model:
            status = "PASS"
            details = "SECURITY.md policy and security design/threat model documentation present."
            remediation = None
        elif has_security_md:
            status = "WARN"
            details = "SECURITY.md is present, but no explicit Threat Model or DPIA document was found."
            remediation = "Document system threats (STRIDE/LINDDUN) and data privacy impact assessment (DPIA) under docs/threat-model.md."
        else:
            status = "FAIL"
            details = "Missing SECURITY.md vulnerability reporting policy and threat modeling documentation."
            remediation = "Create SECURITY.md with coordinated disclosure contacts and document security context per NCSC Secure by Design Principle 1."

        self.results.append(
            CheckResult(
                id="SBD-01-THREAT-CONTEXT",
                pillar="SbD",
                criterion="SbD Principle 1 (Understand security context) & GDS Point 9 (Protect users' privacy)",
                title="Threat Modeling & Security Vulnerability Policy",
                status=status,
                details=details,
                remediation=remediation,
            )
        )

    # 7. TCoP Point 5: Cloud First & Infrastructure as Code
    def _check_cloud_native_configuration(self) -> None:
        has_iac = self._has_file_matching(
            [
                "Dockerfile",
                "docker-compose.y*ml",
                "terraform/**/*.tf",
                "*.tf",
                "k8s/**/*.y*ml",
                "helm/**/Chart.y*ml",
                "sam.y*ml",
                "serverless.y*ml",
            ]
        )
        if has_iac:
            self.results.append(
                CheckResult(
                    id="TCOP-05-CLOUD-FIRST",
                    pillar="TCoP",
                    criterion="TCoP Point 5 (Use cloud first)",
                    title="Cloud-First Architecture & Infrastructure as Code",
                    status="PASS",
                    details="Containerization or Infrastructure as Code (Terraform, Docker, Helm, Serverless) detected.",
                )
            )
        else:
            self.results.append(
                CheckResult(
                    id="TCOP-05-CLOUD-FIRST",
                    pillar="TCoP",
                    criterion="TCoP Point 5 (Use cloud first)",
                    title="Cloud-First Architecture & Infrastructure as Code",
                    status="WARN",
                    details="No declarative Infrastructure as Code or container configurations identified.",
                    remediation="Define cloud infrastructure declaratively using Terraform, OpenTofu, or container manifests adhering to Cloud First guidance.",
                )
            )

    # 8. SbD Principle 4 & 5: Security Headers & Transport Security
    def _check_secure_by_design_controls(self) -> None:
        sec_controls = [
            "Content-Security-Policy",
            "Strict-Transport-Security",
            "X-Frame-Options",
            "X-Content-Type-Options",
            "helmet",
            "secure-headers",
        ]
        has_controls = self._search_file_content(
            ["src/**/*.*", "app/**/*.*", "server/**/*.*", "config/**/*.*", "nginx*.conf"],
            "|".join(sec_controls),
        )
        if has_controls:
            self.results.append(
                CheckResult(
                    id="SBD-04-DEFENSE-IN-DEPTH",
                    pillar="SbD",
                    criterion="SbD Principle 4 (Layered defense) & Principle 5 (Secure data in transit)",
                    title="Defense in Depth: Modern Security Headers & TLS Controls",
                    status="PASS",
                    details="Security header configurations (CSP, HSTS, secure cookies) or middleware detected.",
                )
            )
        else:
            self.results.append(
                CheckResult(
                    id="SBD-04-DEFENSE-IN-DEPTH",
                    pillar="SbD",
                    criterion="SbD Principle 4 (Layered defense) & Principle 5 (Secure data in transit)",
                    title="Defense in Depth: Modern Security Headers & TLS Controls",
                    status="WARN",
                    details="No explicit CSP or HSTS headers detected in application code or server configuration.",
                    remediation="Configure defense-in-depth HTTP response headers (Content-Security-Policy, HSTS, X-Content-Type-Options: nosniff) per NCSC guidance.",
                )
            )


def format_markdown(results: List[CheckResult], target_path: Path) -> str:
    pass_count = sum(1 for r in results if r.status == "PASS")
    warn_count = sum(1 for r in results if r.status == "WARN")
    fail_count = sum(1 for r in results if r.status == "FAIL")
    total = len(results)

    score_pct = int(((pass_count + (0.5 * warn_count)) / total) * 100) if total else 0
    rag_badge = "🟢 GREEN" if score_pct >= 85 else ("🟡 AMBER" if score_pct >= 60 else "🔴 RED")

    lines = [
        f"# UK Government Digital Standards Audit Report",
        f"",
        f"- **Audited Path**: `{target_path}`",
        f"- **Frameworks Covered**: GDS Service Standard, Technology Code of Practice (TCoP), NCSC Secure by Design (SbD)",
        f"- **Overall Assessment**: **{rag_badge}** ({score_pct}% Compliance Score)",
        f"- **Summary**: ✅ **{pass_count} Passed** | ⚠️ **{warn_count} Warnings** | ❌ **{fail_count} Failed**",
        f"",
        f"| ID | Pillar | Standard Criterion | Status | Findings |",
        f"| :--- | :--- | :--- | :---: | :--- |",
    ]

    for r in results:
        status_icon = "✅ PASS" if r.status == "PASS" else ("⚠️ WARN" if r.status == "WARN" else "❌ FAIL")
        lines.append(f"| `{r.id}` | **{r.pillar}** | {r.criterion} | {status_icon} | {r.details} |")

    lines.append("")
    failures = [r for r in results if r.status in ("WARN", "FAIL") and r.remediation]
    if failures:
        lines.append("## 🛠️ Required Remediations & Action Items")
        lines.append("")
        for f in failures:
            prefix = "⚠️ [RECOMMENDED]" if f.status == "WARN" else "❌ [MANDATORY]"
            lines.append(f"### {prefix} {f.title} (`{f.id}`)")
            lines.append(f"- **Finding**: {f.details}")
            lines.append(f"- **Remediation**: {f.remediation}")
            lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Audit codebase for UK Government Digital Standards compliance.")
    parser.add_argument("--target", "-t", default=".", help="Root directory of target repository to audit")
    parser.add_argument("--format", "-f", choices=["text", "markdown", "json"], default="markdown", help="Output format")
    args = parser.parse_args()

    target_dir = Path(args.target).resolve()
    if not target_dir.exists():
        print(f"Error: Target path {target_dir} does not exist.", file=sys.stderr)
        sys.exit(1)

    auditor = GovUKStandardsAuditor(target_dir)
    results = auditor.run_all()

    if args.format == "json":
        print(json.dumps([asdict(r) for r in results], indent=2))
    elif args.format == "markdown":
        print(format_markdown(results, target_dir))
    else:
        for r in results:
            print(f"[{r.status}] {r.pillar} | {r.id}: {r.title} - {r.details}")

    has_fail = any(r.status == "FAIL" for r in results)
    sys.exit(1 if has_fail else 0)


if __name__ == "__main__":
    main()
