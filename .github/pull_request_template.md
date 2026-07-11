## Summary

Describe the user problem and the smallest coherent change.

## Evidence

- [ ] Added or updated a minimal fixture
- [ ] Added positive and negative tests
- [ ] Verified text and JSON output when the CLI contract changed
- [ ] Cited a primary source for normative compatibility/accessibility claims

## Compatibility

List affected clients, frameworks, Python versions, browsers, schema fields, and known valid exceptions.

## Validation

```text
python -m unittest discover -s tests -v
```

- [ ] Skill structure validates
- [ ] Plugin paths and manifest validate
- [ ] No credentials, generated reports, caches, or user project files are included
- [ ] Filesystem-boundary and report-privacy tests cover any auditor I/O change
- [ ] Workflow actions remain pinned to full commit SHAs and CI packages remain hash-locked
- [ ] English and Chinese public documentation remain aligned
