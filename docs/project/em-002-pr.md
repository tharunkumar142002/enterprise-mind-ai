# EM-002 final commit and pull-request review

Reviewed 2026-10-12 on `feature/EM-002-data-collection`.
**Ready for owner review of the collection change. Indexing and public demo remain
BLOCKED.** This is a local draft; nothing is staged, committed, pushed or published.

## Recommended commit message

```text
feat(data): add controlled enterprise collection and synthetic HR (EM-002)
```

## Proposed pull-request title

EM-002: collect licensed enterprise seed data and reproducible fictional HR

## Proposed pull-request description

Stage 1 previously had a scaffold and dataset plan. This change adds a
standard-library Python 3.12 collection pipeline with reviewed source metadata,
explicit approval and exact-URL allowlisting, bounded HTTPS transfers, redirect
rejection, immutable SHA-256 artifacts, provenance and preserved license notices.
The local inventory now covers six domains: five public-source files and five
deterministic fictional HR policies. Runtime datasets remain ignored; the PR
contains code, templates, source metadata, license resources, tests and docs.

The collector defaults to an offline dry run. Bitext retains its publisher
checksum pin, 20 MiB cap, hybrid-synthetic classification and CDLA-Sharing
obligations. Other sources retain 5 MiB caps. GitLab remains blocked and
unapproved. GovInfo is the 260-page U.S. federal July 2025 historical edition,
not current 2026 law. The original fourteen-stage roadmap is unchanged.

Validation on Python 3.12.10: **82 tests executed, 81 passed, one skipped** because
the host disallows creating a real symlink. Manifest validation, read-only HR
reproduction and all five preserved license/provenance bundles pass. All 28
runtime files are ignored and unchanged. No tracked ignored/runtime files or
collected contact values/real credentials were found in proposed commit files.
`git diff --check` passes; existing LF-to-CRLF advisories remain.

Collection approval does not authorize indexing, training or publication. The
[open mandatory gates](backlog.md) require exclusion of 30 Bitext records until
individually cleared; exclusion of the LibreOffice contact passage or a whole
document hold; validated finance PDF extraction; preserved HR fictional and
`internal_demo` labels; and separate intended-use/licensing/publication review.
These future controls are documented, not implemented by this PR. No preprocessing,
chunking, embeddings, RAG, public-demo approval or new dependencies are included.

## Review evidence and limitations

- Reviewed the manifest/schema, CLI, transport/storage controls, license bindings,
  distribution preparation, HR generator/templates, tests, packaging and docs.
  No collection-scope blocker was found in the reviewed change. This is not a
  production certification or an exhaustive security/privacy/rights audit.
- The existing interpreter required approved access outside the agent sandbox;
  no environment repair or package installation was performed. Tests used
  synthetic fixtures, network guards and temporary directories, not real downloads.
- The complete suite ran in 6.136 seconds. The real-symlink integration case is
  the one skipped test; mocked path checks ran. Packaging/build tools were not
  installed, and a distributable package was not built.
- Offline verification recalculated hashes, validated the current source manifest,
  checked archived manifests and all license/notice/provenance references through
  `prepare_distribution`, and compared all six generated HR files with deterministic
  output. Bundle preparation stayed in memory and did not approve or export data.
- The 22 raw files and six synthetic runtime files retained their hashes, byte
  sizes and modification times. The source manifest and roadmap also retained
  all three properties. The original Python dataset was untouched.
- Git safety: all 28 runtime files are ignored, with zero tracked runtime files,
  zero tracked ignored files and an empty index. Thirteen representative ignore
  probes covered environments, secrets/credentials, raw/private/synthetic data,
  weights and artifacts. `.gitignore` and `.dockerignore` were not weakened.
- Candidate screening checked text/file types, paths, common credential/key
  patterns, contact patterns and overlap with collected email-like values.
  Five pattern hits were confined to deliberate rejection fixtures in
  `tests/test_manifest.py` and `tests/test_synthetic_hr.py`: reserved example
  domains/phone and visibly fictional credentials. No contact values were copied
  from Bitext or LibreOffice into reports or fixtures.
- Mandatory public copyright/contributor credits remain in license resources.
  Those legal notices are intentional attribution, not private employee records.
  Pattern scanning is not proof that arbitrary text contains no sensitive data;
  re-review any subsequent candidate changes before staging.
- HTTP Content-Type checks are not document sanitization. Raw HTML is untrusted;
  PDF extraction fidelity and downstream authorization remain open. The 30-record
  privacy list addresses reviewed findings, not all possible PII in the corpus.
- `git diff --check` covers tracked modifications. Candidate text and local-link
  checks passed with the two pinned-license formatting exceptions below. Four documentation EOF blank lines were
  cleaned up. Two pinned upstream texts (`CC-BY-4.0.txt`, `CC-BY-SA-4.0.txt`) retain
  their original trailing blank lines and decorative separators; do not trim or
  reformat them, as their hashes bind the reviewed license/provenance artifacts.
  Git may flag those legal-text EOF blank lines when they are later staged.

Reproduction commands for offline checks (no acquisition):

```powershell
$env:PYTHONPATH = (Resolve-Path .\src).Path
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -B -m enterprise_mind.ingestion validate
.\.venv\Scripts\python.exe -B -m enterprise_mind.ingestion.synthetic_hr --check
git status --short --untracked-files=all
git diff --check
```

## Final files proposed for commit

**42 files: four tracked modifications and 38 new files.** This explicit list is
for review, not an instruction to stage the entire working tree. The current
finalization adds `backlog.md` and this draft, updates seven documentation files
and trims EOF blank lines in two other documentation files; collection code,
tests, licenses, templates and source approvals retain
the earlier EM-002 implementation.

Tracked modifications:

```text
README.md
docs/data/dataset-plan.md
docs/project/requirements.md
pyproject.toml
```

New files:

```text
data/LICENSES.md
data/README.md
data/sources.yaml
docs/data/collection.md
docs/data/final-data-quality-review.md
docs/data/source-readiness.md
docs/data/synthetic-hr.md
docs/project/backlog.md
docs/project/em-002-pr.md
src/enterprise_mind/ingestion/__init__.py
src/enterprise_mind/ingestion/__main__.py
src/enterprise_mind/ingestion/collector.py
src/enterprise_mind/ingestion/distribution.py
src/enterprise_mind/ingestion/licenses/CC-BY-4.0.txt
src/enterprise_mind/ingestion/licenses/CC-BY-SA-3.0.txt
src/enterprise_mind/ingestion/licenses/CC-BY-SA-4.0.txt
src/enterprise_mind/ingestion/licenses/CDLA-Sharing-1.0.txt
src/enterprise_mind/ingestion/licenses/PSF-2.0.txt
src/enterprise_mind/ingestion/licenses/US-Government-Work.txt
src/enterprise_mind/ingestion/licenses/bitext-notices.txt
src/enterprise_mind/ingestion/licenses/gitlab-notices.txt
src/enterprise_mind/ingestion/licenses/gnome-notices.txt
src/enterprise_mind/ingestion/licenses/govinfo-notices.txt
src/enterprise_mind/ingestion/licenses/libreoffice-notices.txt
src/enterprise_mind/ingestion/licenses/python-copyright.txt
src/enterprise_mind/ingestion/licensing.py
src/enterprise_mind/ingestion/manifest.py
src/enterprise_mind/ingestion/reviewed_sources.py
src/enterprise_mind/ingestion/synthetic_hr.py
src/enterprise_mind/ingestion/templates/hr-v1.json
tests/collection_fixtures.py
tests/test_collection.py
tests/test_collection_cli.py
tests/test_collection_transport.py
tests/test_enterprise_licenses.py
tests/test_license_preservation.py
tests/test_manifest.py
tests/test_synthetic_hr.py
```

Do not include `data/raw/`, `data/synthetic/`, downloaded/private datasets,
provenance runtime sidecars, temporary review extracts/renderings, `.venv/`,
actual `.env`/secret/credential files, caches, model weights or generated indexes.
Keep those existing runtime artifacts intact locally. Reviewed source metadata
and bundled legal texts listed above are deliberate exceptions to runtime data.

## Outstanding follow-up tickets

All five local backlog tickets remain **OPEN**: EM-002-F01 (Bitext exclusions),
F02 (LibreOffice passage/hold), F03 (finance extraction), F04 (HR labeling), and
F05 (separate use/rights approvals). Full evidence, snapshot-bound locators and
acceptance criteria are in [the backlog](backlog.md). No external issues were
created. Owner review is required before committing or taking a later-stage action.
