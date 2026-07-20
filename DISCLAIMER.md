# Disclaimer

[简体中文](DISCLAIMER.zh-CN.md)

Last updated: 2026-07-11

AdaptiveUI-SKILL (the “Project”) is an open-source developer tool for reviewing and improving web-interface code. This notice clarifies the Project's limits; it does not replace or modify the [Apache License, Version 2.0](LICENSE).

## Tooling purpose, not professional advice

The Project provides automated heuristics, workflow guidance, examples, and technical recommendations. Its output is not legal advice, a legal opinion, security advice tailored to a particular threat model, an accessibility audit by an accredited specialist, or a substitute for qualified professional review.

References to WCAG, browser support, security practices, operating systems, frameworks, or other standards and products are informational. They do not establish certification, regulatory compliance, endorsement, or guaranteed compatibility.

## No warranty or certification

The Project is provided on an “AS IS” basis under Apache-2.0, without warranties or conditions beyond those required by applicable law. Static rules and automated tests can produce false positives, false negatives, incomplete findings, or environment-specific results.

The Project does not guarantee that:

- an audited or modified interface is defect-free, secure, accessible, standards-compliant, or suitable for production;
- every browser, device, assistive technology, framework version, localization, or deployment environment will behave identically;
- a report is complete or that the absence of findings means the absence of risk;
- future versions will remain compatible with every existing configuration or integration.

Use of the Project does not constitute penetration testing, independent security assessment, legal review, WCAG certification, or any other formal certification.

## User responsibility

You are responsible for deciding whether and how to use the Project and for reviewing its output before applying or publishing changes. Maintain appropriate backups, test in the environments you support, and obtain any professional advice required for your circumstances.

You are also responsible for:

- having permission to inspect, process, modify, or share the target source code and related reports;
- complying with applicable laws, contracts, licenses, privacy obligations, organizational policies, and platform terms;
- reviewing generated changes, configuration, dependencies, and commands before execution;
- avoiding the use of untrusted build scripts, browser profiles, credentials, or production systems without separate authorization and safeguards.

## Source code and report privacy

The bundled static auditor does not itself access the network or execute scanned project code. However, reports can contain filenames, project structure, rule messages, and short source excerpts. Use `--redact-evidence` when source disclosure is unnecessary, and review all output before sharing it.

The agent client, editor, browser controller, CI provider, hosting platform, or other software used with the Project may have separate data handling, telemetry, retention, authentication, and privacy terms. This Project does not control or make representations for those services.

## Third-party names, links, and materials

Names such as OpenAI, Codex, W3C, WCAG, browser names, operating systems, and framework names are used only to describe compatibility, standards, or integrations. All product names and trademarks belong to their respective owners. Their inclusion does not imply affiliation, sponsorship, certification, or endorsement.

External links and third-party tools are provided for convenience. Their availability, content, security, licensing, and terms are controlled by their respective operators. Review those terms independently before use.

## Security reports

No software can be guaranteed free of vulnerabilities. Report suspected Project vulnerabilities privately according to [SECURITY.md](SECURITY.md), and do not publish credentials, exploit details, or private source code in a public issue.

## Relationship to the license and translation

The Apache License, Version 2.0 controls the licensing, use, reproduction, and distribution of the Project. If this notice conflicts with the License, the License controls. The English and Simplified Chinese versions are intended to communicate the same boundaries; if their wording differs, refer to this English version and the License text.

This notice is general project information and is not a legal opinion about any particular person, organization, jurisdiction, or use case.
