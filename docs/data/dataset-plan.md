# Multi-domain enterprise dataset plan

## Purpose and incremental scope

Support enterprise knowledge and workflow automation across six domains using a
mixture of appropriately licensed public documents and clearly labeled fictional
enterprise records. Kubernetes is one possible technical source, not the product
boundary. EM-001 defines this plan only: no downloads, scraping, model acquisition
or generated dataset files were included in that scaffold.

EM-002 adds [data/sources.yaml](../../data/sources.yaml) and manifest-driven
collection code. Python, GNOME, GovInfo, LibreOffice and Bitext are collected and
verified with license bundles. GitLab remains unapproved and requires a privacy
decision. HR is supplied by five original, versioned fictional policies generated
locally; this task neither downloads nor changes the existing raw artifacts.
See the [complete inventory and verification findings](../../data/README.md),
[collection guide](collection.md), [source review](source-readiness.md) and
[synthetic HR guide](synthetic-hr.md). The
[final quality review](final-data-quality-review.md) now records the findings;
[mandatory follow-up gates](../project/backlog.md) specify the required privacy
exclusions, validated PDF extraction, HR labeling and separate use/rights approval.
Collection approval does not authorize indexing or publication. Six-category
coverage is bounded seed coverage, not a complete enterprise knowledge base.

## Domain coverage

| Domain | Public-source candidates (review before acquisition) | Fictional enterprise records |
| --- | --- | --- |
| HR policies and employee handbooks | Employer-facing guides or policy templates with explicit reuse permission | Leave, remote work, onboarding, benefits, handbook revisions and approval workflows |
| IT troubleshooting and security manuals | License-reviewed OSS user/admin documentation | VPN/access troubleshooting, acceptable use, incident runbooks and security escalation |
| Finance and reimbursement policies | Public travel/expense guidance with source-specific permission | Expense limits, reimbursement timelines, receipt rules and approval matrices |
| Product manuals and FAQs | Reusable OSS product documentation | Fictional EnterpriseMind product guide, release notes, limitations and FAQs |
| Customer support records and tickets | Explicitly licensed, sanitized ticket corpora only; otherwise use fictional records | Multi-turn tickets, troubleshooting history, escalation, status transitions and resolution notes |
| Technical documentation | License-reviewed Python, PostgreSQL and Kubernetes documentation | Fictional service/API specifications, architecture decisions and team runbooks |

Candidates are not approved datasets. Verify the exact source version, content
license, third-party exclusions, attribution requirements and permission for each
intended use (redistribution, indexing and separately training). If a candidate
cannot be cleared, substitute an explicitly fictional record rather than copying
it. Do not scrape real employee/support data or assume public tickets are safe.

Primary reference for one candidate:
[Kubernetes website license](https://github.com/kubernetes/website/blob/main/LICENSE).
Other sources require independent review before adoption.

## Fictional-record contract

- Use a fictional organization and departments. The current HR edition uses roles
  only and contains no employee records or personal identifiers.
- Put `FICTIONAL ENTERPRISE RECORD - FOR DEMONSTRATION ONLY` in each document.
- Current HR policies contain no contact values, including example emails/phones.
  Any later contact fixtures must use reserved examples and separate review.
- Record authoring method, schema version and `is_fictional=true` in metadata.
- Define fictional HR/finance rules as demo policies, not authoritative guidance.
- Keep the current HR edition internally consistent using shared rule definitions.
  Future evaluation fixtures may include conflicting/expired revisions, duplicates,
  ambiguous or unanswerable questions, kept separate from this active edition.
- At the evaluation stage, create controlled malicious-text fixtures;
  label them explicitly and keep them distinct from ordinary knowledge records.

## Provenance and permissions

Every source/document records:

- Stable document ID, domain, source classification and language. The public
  collector uses `public_document` / `public_synthetic_dataset`; local HR uses
  `project_authored_synthetic`, explicitly distinguished from publisher synthetic data.
- Source URL or authoring provenance, revision, acquisition date and checksum.
- License identifier/link, attribution text and allowed uses.
- Department and visibility/access classification. Tenant/role enforcement and
  retention controls remain future stages; `internal_demo` alone is not authorization.
- Effective/expiry dates and superseded-document references where relevant.
- Fictional status and evidence/citation anchors.

Keep public source research metadata in `data/sources.yaml`; it is not a blanket
license approval. Local HR provenance uses versioned templates and a generated
manifest without a fictional HTTPS URL or a public-collector approval bypass.
The [license index](../../data/LICENSES.md) identifies preserved terms and notices.
Downloaded files, parsed records, training corpora, uploads and vector indexes live
under ignored `data/` paths. Small reviewed synthetic test fixtures can live under
`tests/fixtures/` when tests require them. EM-002 tests use in-memory synthetic
fixtures and temporary directories. Collected files live under `data/raw/`, and
generated HR under `data/synthetic/hr/v1/`; both are ignored and excluded from
container contexts. Only templates, code and reviewed inventory/docs belong in Git.

## Evaluation and training separation

Begin with a bounded corpus on existing hardware. Ensure every domain has
reviewed answerable, unanswerable and permission-boundary questions. Split at
document family/source revision and ticket-thread level to reduce leakage.
Fine-tuning examples cannot include held-out questions, answer labels or their
derived training duplicates. Knowledge passages can support retrieval evaluation;
the held-out questions/reference judgments remain excluded from tuning.

Track dataset, prompt, model, embedding and index versions with each run. Measure
retrieval relevance, citation support, abstention and workflow success. Evaluate
unauthorized retrieval and tool attempts separately, including cross-tenant and
cross-role cases. Real private company data is outside the initial corpus plan.
