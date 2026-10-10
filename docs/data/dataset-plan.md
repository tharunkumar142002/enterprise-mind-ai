# Multi-domain enterprise dataset plan

## Purpose and EM-001 limit

Support enterprise knowledge and workflow automation across six domains using a
mixture of appropriately licensed public documents and clearly labeled fictional
enterprise records. Kubernetes is one possible technical source, not the product
boundary. EM-001 defines this plan only: no downloads, scraping, model acquisition
or generated dataset files are included.

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

- Use a fictional organization, departments, products and employee identifiers.
- Put `FICTIONAL ENTERPRISE RECORD - FOR DEMONSTRATION ONLY` in each document.
- Use reserved example domains such as `example.com`; never real contact data.
- Record authoring method, schema version and `is_fictional=true` in metadata.
- Define fictional HR/finance rules as demo policies, not authoritative guidance.
- Include conflicting revisions, expired policies, duplicate documents, ambiguous
  questions, unanswerable questions and cross-department workflows.
- Create controlled malicious-text fixtures for prompt-injection evaluation;
  label them explicitly and keep them distinct from ordinary knowledge records.

## Provenance and permissions

Every source/document records:

- Stable document ID, domain, source kind (`public` or `fictional`) and language.
- Source URL or authoring provenance, revision, acquisition date and checksum.
- License identifier/link, attribution text and allowed uses.
- Tenant, department, permitted roles, visibility and retention classification.
- Effective/expiry dates and superseded-document references where relevant.
- Fictional status and evidence/citation anchors.

Keep reviewed metadata in future `data/sources.yaml` and `data/LICENSES.md`.
Downloaded files, parsed records, training corpora, uploads and vector indexes live
under ignored `data/` paths. Small reviewed synthetic test fixtures can live under
`tests/fixtures/` when tests require them. No such directories are created yet.

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
