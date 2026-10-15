# EnterpriseMind AI requirements

## Product scope

Build an enterprise knowledge and workflow automation platform that answers
questions from authorized sources, returns citations, abstains when evidence is
insufficient and executes approved, auditable workflows. Support HR policies and
handbooks, IT troubleshooting and security, finance/reimbursements, product
manuals/FAQs, customer support tickets and technical documentation.

## Functional requirements for later stages

| ID | Requirement |
| --- | --- |
| FR-01 | Ingest approved documents with provenance, revision, checksum, domain and tenant/access metadata; deduplicate and support update/deletion. |
| FR-02 | Retrieve only authorized chunks; produce cited answers and explain insufficient evidence without inventing policy. |
| FR-03 | Compare baseline, framework-based and advanced RAG using the same domain contracts and held-out cases. |
| FR-04 | Provide bounded LangGraph workflows, typed tool calling, MCP integration and multi-agent coordination. |
| FR-05 | Require scoped authorization and explicit confirmation for mutating tools; make retries idempotent where possible. |
| FR-06 | Evaluate retrieval, answers and agents; keep training, development and held-out evaluation data separate. |
| FR-07 | Expose validated FastAPI endpoints, streamed answers, ingestion status and agent audit/run views; offer Streamlit and React interfaces in sequence. |
| FR-08 | Store documents/metadata/vectors through interchangeable adapters; implement migrations, deletion and backup/restore. |
| FR-09 | Track model, prompt, source and index versions with redacted operational and evaluation telemetry. |

## Engineering constraints

- Python 3.12 is the initial supported version (`>=3.12,<3.13`).
- Zero additional spend: existing compute, local OSS defaults and no billable
  fallback. Hosted alternatives need authorization and verified free limits.
- Keep every technology/concept in the inventory; selecting a primary option
  does not require implementing or installing every alternative.
- Preserve `.git/` and `.venv/`; do not reuse another RAG project's code.
- No dependency installs, dataset/model downloads, commits, pushes or deployment
  during EM-001.
- Model/data licenses are reviewed per selected artifact and source. Public
  visibility alone does not grant reuse or training permission.
- Secrets and private/generated data stay outside Git and container contexts.
- Tenant isolation applies to retrieval, caches, sessions, checkpoints and tools;
  authentication establishes scope before processing caller-supplied identities.
- Treat source material and tool output as untrusted; redact logs and telemetry.
- Later APIs need request/upload limits, timeouts, cancellation and safe failures.
- Production latency/throughput targets will be set after measuring available
  hardware. No unsupported SLA or universal CPU/GPU performance claim is made.

## EM-001 deliverables and acceptance

1. `.gitignore` and `.dockerignore` protect secrets, `.venv`, data and models.
2. README and AI/contributor instructions describe the active scope honestly.
3. `pyproject.toml` declares Python 3.12, a `src/` package and no runtime dependencies.
4. `.env.example` contains blank placeholders; there is no active settings loader.
5. `enterprise_mind` imports without third-party dependencies or output.
6. Standard-library smoke tests check isolated import and metadata/version parity.
7. Documentation preserves the exact fourteen stages and complete technology list.
8. The dataset plan covers all six domains using licensed public sources plus
   clearly labeled fictional records; no dataset is acquired yet.
9. Future modules are documented, not instantiated as empty trees.
10. Report added/modified files, ignore checks, documentation checks and runtime
    checks. If Python is unavailable, identify unexecuted checks explicitly.

## Runtime verification prerequisite

The existing environment records Python 3.12.10 but its base interpreter was
unavailable at inspection. No environment repair is included in EM-001. A working
Python 3.12 interpreter is required to execute smoke tests and parse project TOML.

## EM-002 first-increment acceptance criteria

- Research one bounded public source candidate for each of the six enterprise
  domains. Record actual URLs and primary evidence; uncertain licenses remain
  pending review. Do not collect private/confidential material.
- Version `data/sources.yaml` with explicit categories/formats, source revisions,
  license/evidence status and approval metadata. No real approvals are granted
  during the initial implementation; the exact-URL download allowlist starts empty.
  Later source-specific approval requires explicit user instruction and completed
  source/license review. Python, GNOME, GovInfo, LibreOffice and Bitext have since
  been explicitly authorized, collected and verified; GitLab remains blocked.
- Validate required fields/types, duplicate IDs/URLs, safe identifiers and formats.
- Provide offline validation and a dry-run-first command. Real downloads require
  reviewed source/license, recorded approval, exact allowlisting and explicit
  execution. Final user review occurs before any actual download.
- Bound HTTPS requests and reads, reject redirects/private destinations, confine
  paths, enforce byte limits and clean partial transfers. Store SHA-256 snapshots,
  separate source provenance, manifest fingerprints and duplicate-content status.
- Record source URL, document ID, title, category, UTC collection timestamp,
  license, checksum, content/source versions and public access classification.
- Use network-free synthetic tests and existing tooling only. Keep the roadmap
  unchanged; no installation, chunking, embeddings, commits, pushes or deployment.

## EM-002 synthetic HR completion criteria

- Complete six-category seed coverage using five original fictional HR policies:
  annual/sick leave, onboarding, remote work, attendance/hours and offboarding.
- Use versioned templates, shared policy definitions and deterministic UTF-8 JSON
  output under ignored `data/synthetic/hr/v1/`; no model or network calls.
- Record unique IDs, title, category, version, effective date, owner, access
  classification, fictional provenance, content and checksums. Use roles only;
  exclude employee identities, contact details, credentials and private data.
- Keep synthetic source classification separate from public-document approvals.
  Preserve the HTTPS collector, exact allowlist, blocked GitLab and existing raw
  artifacts. Reject conflicting generated files rather than replacing them.
- Test metadata, IDs, reproducibility, classification, shared-rule consistency,
  contact/credential exclusions and safe immutable output using synthetic fixtures.
- Verify the existing five sources offline; record content/privacy/license issues
  honestly before future preprocessing. Review is not permission to index or publish.

## EM-002 finalization and mandatory follow-up gates

Collection acceptance is separate from indexing and publication acceptance.
`collection_for_rag` authorizes controlled acquisition only. No preprocessing,
indexing, training or public-demo permission is implied by source approval,
public classification, a preserved license or successful bundle verification.

The [local backlog](backlog.md) records open, mandatory acceptance criteria:

- EM-002-F01: exclude all 30 flagged Bitext records until individually cleared.
- EM-002-F02: exclude the LibreOffice contact passage or hold the whole document.
- EM-002-F03: require validated extraction of the 260-page July 2025 finance PDF,
  preserving its U.S. federal jurisdiction and historical-edition context.
- EM-002-F04: preserve fictional HR labels and `internal_demo` classification.
- EM-002-F05: check rights, attribution and separate intended-use/publication
  permission for each snapshot/derivative before any downstream approval.

These follow-ups are not implemented by EM-002. Preserve every raw/runtime
artifact and the existing GitLab block. The final review prepares a commit/PR
description; staging, committing, pushing, merging and publication require later
user authorization. The original fourteen-stage roadmap remains unchanged.
