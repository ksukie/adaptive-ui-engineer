# Release checklist

Use this checklist for each public release. It separates repository readiness from claims that require independent review.

## Identity, rights, and documentation

- [ ] Confirm that `ksukie` is the intended public author and repository owner everywhere it appears.
- [ ] Confirm that the year, release version, project URLs, installation names, and marketplace names are correct.
- [ ] Confirm that every source file and project-owned asset can be released under Apache-2.0.
- [ ] Preserve required third-party notices if any third-party material is added. Do not create a `NOTICE` file unless there is content that actually requires it.
- [ ] Read the English and Chinese READMEs side by side and verify that their behavior and compatibility claims agree.
- [ ] Read `DISCLAIMER.md` and `DISCLAIMER.zh-CN.md` side by side; confirm that their warranty, certification, privacy, third-party, user-responsibility, license-priority, and trademark boundaries agree.
- [ ] Confirm that the independent-project and trademark disclaimer is acceptable.

## Source and privacy review

- [ ] Search all text files for credentials, tokens, private URLs, email addresses, local usernames, absolute paths, and copied private source.
- [ ] Confirm that no generated audit reports, screenshots of private projects, caches, virtual environments, browser profiles, build output, or editor metadata are present.
- [ ] Confirm that repository assets contain no active script, remote resource, tracking pixel, or embedded credential.
- [ ] Run the auditor security regression tests on a platform that permits symbolic links; verify the skip/reject behavior and unchanged external target.
- [ ] Review every workflow permission and every external dependency. Action references must be full commit SHAs; Python CI packages must retain hashes.

## Required validation

Run from the repository root:

On Windows where `python` is not registered, substitute `py -3` in the commands below.

```text
python -m unittest discover -s tests -v
python plugins/adaptive-ui-engineer/skills/adaptive-ui-s/scripts/audit_ui.py tests/fixtures/good --format json --redact-evidence --fail-on P1
```

- [ ] Run the suite with Python 3.9, 3.10, and 3.11 locally; let hosted CI cover the documented wider matrix.
- [ ] Run the current Codex Skill Creator structural validator.
- [ ] Run the current Codex Plugin Creator manifest validator.
- [ ] Run the hash-locked open Agent Skills reference validator.
- [ ] Confirm Codex surfaces `Adaptive-UI-S` and `Adaptive-UI-N`, and that each is inactive unless explicitly selected in the current message.
- [ ] Smoke-test S's read-only final review and N's required, scoped post-change style audit without expanding either into a whole-repository review.
- [ ] Confirm that no validation step created caches, reports, temporary packages, or user-project changes in the release tree.
- [ ] Perform one read-only smoke audit of a real interface and record any browser environments that were not tested.

## Repository settings after publication

- [ ] Set default GitHub Actions workflow permissions to read-only and grant write permissions only in the jobs that require them.
- [ ] Enable private vulnerability reporting and verify the link in `SECURITY.md`.
- [ ] Enable Dependabot alerts and security updates.
- [ ] Enable secret scanning and push protection when the repository/account supports them.
- [ ] Confirm that CI and CodeQL complete successfully on the public default branch.
- [ ] Protect the default branch with required reviews and required passing checks appropriate to the maintainer model.
- [ ] Review whether workflow runs from forked pull requests require maintainer approval.
- [ ] Verify issue forms, the pull-request template, license detection, repository description, topics, and release notes in the public UI.

## Claim control

- [ ] Keep “designed compatibility” separate from platforms actually tested for this release.
- [ ] Do not describe static findings as proven runtime defects or claim WCAG conformance from the auditor alone.
- [ ] Do not describe this checklist, CI, CodeQL, or maintainer review as a penetration test, legal review, independent audit, or certification.
- [ ] Record known limitations and unverified environments in the release notes.

## Sign-off

- Release candidate version:
- Test environments:
- Skill validator result:
- Plugin validator result:
- Open Agent Skills validator result:
- Security review date and reviewer:
- Open-source/license review date and reviewer:
- Known residual risks:
