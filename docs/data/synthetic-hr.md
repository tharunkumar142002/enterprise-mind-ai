# EM-002 reproducible fictional HR policies

The fictional **EnterpriseMind Demo Company** has five original policies, edition
1.0.0, effective 2026-10-12. They describe demonstration workflows, not an actual
employer or a statement of applicable employment law. Every document starts with
`FICTIONAL ENTERPRISE RECORD - FOR DEMONSTRATION ONLY`.

## Source and output

- Source template: [hr-v1.json](../../src/enterprise_mind/ingestion/templates/hr-v1.json).
- Generator: [synthetic_hr.py](../../src/enterprise_mind/ingestion/synthetic_hr.py).
- Runtime output: ignored `data/synthetic/hr/v1/`, five JSON documents plus
  `manifest.json`. Each document's `content` is Markdown; no separate extracted
  or chunked files are created.
- Tests: [test_synthetic_hr.py](../../tests/test_synthetic_hr.py), stdlib only.

Templates and generator belong in Git after owner review; generated data does not.
The existing ignore rules already cover raw and synthetic data. Package-data
configuration includes the template for a future authorized package build.
No build, installation, model call, download or external dependency is needed.

| Document ID | Title |
| --- | --- |
| `em-hr-leave-v1` | Annual and Sick Leave Policy |
| `em-hr-onboarding-v1` | Employee Onboarding Policy |
| `em-hr-remote-work-v1` | Remote Work Policy |
| `em-hr-attendance-v1` | Attendance and Working Hours Policy |
| `em-hr-offboarding-v1` | Employee Offboarding Policy |

## Shared policy definitions

All repeated paragraphs use the same clauses and numeric rule values.

| Topic | Fictional rule |
| --- | --- |
| Schedule | Monday-Friday, 09:00-18:00 Asia/Calcutta, 60-minute unpaid break, 8 paid hours/day and 40/full week |
| Core availability | 10:00-16:00, except break, approved leave or documented accommodation |
| Annual / sick leave | Separate allocations of 20 / 10 paid working days per calendar year; joiners prorated by calendar days employed, rounded up to half-day units |
| Annual requests | Five business days' notice; manager approval before absence; urgent cases use documented exceptions |
| Sick absence | Notify as practicable; no prior approval for unexpected illness; no diagnoses or medical documents in the demo |
| Carryover | Up to five annual days, use by end of March; sick days do not carry over or pay out |
| Routine approvals | Manager response within two business days; silence is not approval; People Operations assigns an alternate if needed |
| Onboarding | Orientation/security training in paid time within five business days; review after 30 calendar days |
| Remote work | Up to three approved remote days/week; same work/leave/attendance rules; can begin during onboarding when requirements are met |
| Offboarding | 30 calendar days' routine voluntary notice, unless a written exception; annual allocation recalculated through departure, positive unused earned annual balance paid out; sick leave not paid out |
| Access / assets | Access ends at end of final working day (or an authorized earlier security decision); assets returned within three business days without extending account access |

The templates define holidays, calendar/business-day distinctions, proration,
exceptions, leave during notice and negative-balance manual review consistently.
No intentionally contradictory revisions or employee-specific exceptions are part
of this active edition. Future evaluation conflict fixtures must be kept separate.

## Metadata and provenance

Each document records schema version, unique ID, title, `human_resources`
category, version, effective date, owner `People Operations (fictional)`,
company, language, access classification `internal_demo`, fictional flag,
used rule values, Markdown content and content SHA-256.

The source kind is `project_authored_synthetic`. Provenance explicitly describes
Codex-assisted original authoring with human review pending, deterministic
template generation, allowed demonstration use `collection_for_rag`, generator
version/hash, canonical template hash/path and fixed authored date. `source_url`
is null, because there is no publisher URL for this original local material.
No real employee names, identifiers, emails, phones, credentials or confidential
records are used. The terms reference roles only.

The manifest records each full JSON file's SHA-256 and byte size. Template
fingerprinting uses sorted UTF-8 JSON; generator hashing normalizes source line
endings. Output is UTF-8 with LF, sorted keys and deterministic document order.
No generation timestamp, random seed or nondeterministic model output is included.
The same generator and templates reproduce the same bytes across clean checkouts.

`internal_demo` is descriptive metadata, not implemented tenant/access enforcement.
External publication/license choice for original HR material needs owner review;
no third-party license is silently applied. See [license index](../../data/LICENSES.md).

## Commands

From the repository root, using the existing Python 3.12 environment:

```powershell
$env:PYTHONPATH = (Resolve-Path .\src).Path

# Default: inspect the plan, without writes or network.
.\.venv\Scripts\python.exe -B -m enterprise_mind.ingestion.synthetic_hr

# Explicit local generation, for an empty output or an identical existing edition.
.\.venv\Scripts\python.exe -B -m enterprise_mind.ingestion.synthetic_hr --write

# Read-only verification: every expected file must exist and match exact bytes.
.\.venv\Scripts\python.exe -B -m enterprise_mind.ingestion.synthetic_hr --check

# Complete existing and new test suite.
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -v
```

The edition is already generated in this workspace. Repeating `--write` with
identical files preserves their bytes and modification times. Differing files,
unexpected entries, symlinks/junctions or unsafe paths fail before publication.
An exclusive lock and temporary-file/atomic hard-link publication prevent
overwriting artifacts. Files are capped at 128 KiB. Output is confined to the
synthetic edition directory and never goes through the network collector.

Do not edit an existing generated record to change a policy. Review source
template/code changes as a new edition and implement its new IDs/output path;
the current generator deliberately supports only v1. On interruption, inspect a
remaining lock/staging file and active writers before separately authorized
recovery. The generator does not delete unknown files or silently repair corruption.

## Validation scope

Eighteen HR tests cover required metadata, exact IDs, source classification,
byte reproducibility, shared rules, arithmetic/range constraints, conflicting
rendered text, contact/credential-like strings and immutable path/lock behavior.
The full suite reports 82 executed, 81 passed, one host-limited symlink skip.

These are checks against a closed, reviewed template edition, not a general
natural-language contradiction detector or universal PII detector. Changing the
source templates still requires human content review. Regex checks alone cannot
prove that arbitrary future prose has no personal information.

Existing raw datasets, public approval manifest, GitLab block, collection security
checks and the original fourteen-stage roadmap are preserved. No preprocessing,
chunking, embeddings, training or publication is implemented in this increment.
