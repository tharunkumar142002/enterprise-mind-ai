# EM-002 final dataset quality review

2026-10-12 | `feature/EM-002-data-collection` | Local review only.

**Readiness: BLOCKED for indexing/public-demo sign-off.** Collection and technical
validation pass. The owner's EM-002 finalization instruction makes the privacy,
extraction, labeling and rights follow-ups **mandatory**; see the
[open backlog gates](../project/backlog.md). No source was filtered, modified,
downloaded or newly approved by this review.

## Privacy findings

All 57 previously flagged occurrences were inspected using local domain, mailbox
role and surrounding-context checks. No contact values or source sentences were
printed. No external lookup, delivery test or contact attempt was performed.

| Findings | Clearly synthetic | Public business contact | Potential personal information | Uncertain |
| --- | ---: | ---: | ---: | ---: |
| Bitext emails (55) | 26 | 0 | 0 | 29 |
| Bitext phone (1) | 0 | 0 | 0 | 1 |
| LibreOffice email (1) | 0 | 1 | 0 | 0 |

Zero positively identified personal-information findings does not clear uncertain
values or establish that unflagged text is PII-free.

**Bitext locators:** source `support-bitext-v11`, snapshot SHA-256
`6f81102b0100b97b8468eb04368033a23206bf1fde9d53500d5806ec1001a434`.
Numbers are **1-based parsed CSV data-record ordinals, excluding the header**,
not physical line numbers. Every email is occurrence 1 in `response`.

- **Clearly synthetic (26):** 8014, 8196, 9893, 11666, 18093, 18201, 20904, 20996, 21046, 21068, 21191, 21192, 21227, 21369, 21373, 21415, 21426, 21446, 21480, 21585, 21653, 21655, 21727, 21828, 21845, 21988.
  These addresses use reserved example domains. This clears the email finding
  only; record 18201 also contains the uncertain phone.
- **Uncertain emails (29):** 21324, 21328, 21375, 21554, 21784, 21933, 21986, 21994, 22054, 22175, 22228, 22259, 22287, 22320, 22445, 22516, 22525, 22602, 22632, 22646, 22697, 22727, 22760, 22765, 22768, 22779, 22784, 22795, 22864.
  Non-reserved domains lack sufficient ownership evidence. Generic support or
  feedback context does not prove that an address is fictional or authorized.
- **Uncertain phone:** record **18201**, `response`, occurrence 1. The 11-digit
  contact-shaped value could not be established as an explicitly reserved
  example. Publisher synthetic classification alone does not prove non-routability.

**Flag all 29 uncertain-email records plus 18201 for exclusion from future RAG
indexing: 30 distinct complete records, until individually cleared.** This is a
mandatory follow-up gate. Its future implementation must preserve snapshot hash,
ordinal, reason and change provenance. No filtering is implemented by this report. Preserve Bitext's
hybrid-synthetic origin and CDLA-Sharing obligations.

**LibreOffice:** source `product-libreoffice-writer`, snapshot SHA-256
`690bdc861c56fb4a543624cb33c2f29a6d4cb4240e51983de0339899a1793371`.
The single visible email and matching `mailto:` link in the Preface's
Feedback/documentation context identify a documentation-role contact on a Document
Foundation domain, published by the official source. Classification: **public
business contact**. Exclude that contact-routing passage from future indexing,
or hold the whole document until exclusion can be validated. Retain required
legal attribution in notices/provenance; the raw HTML remains unchanged.

## Finance PDF

| Check | Finding |
| --- | --- |
| Identity/count | PASS: Subtitle F, Federal Travel Regulation System, 41 CFR; **260 PDF pages**, confirmed by the installed Windows PDF reader and independent page-tree count; no password. It is the subtitle excerpt, not the full volume. |
| Edition | PASS: visible `7-1-25 Edition` headers agree with preserved GovInfo edition metadata `2025-07-01`. U.S. federal historical reference, **not current 2026 law or company policy**. |
| Readability | PASS on visually inspected pages **1, 2, 3, 4, 15, 44, 65, 125, 130, 195, 223, 257, 260**. Body/table text is legible; pages 2 and 4 are blank separators. |
| Text-layer diagnostic | All 260 direct page-content streams decoded in memory without decompression errors; text operators present. This limited diagnostic is not a general parser certification or full-page visual review. |
| Layout | Two-column prose; full-width table between columns (page 44); multiple tables with footnotes and required/discretionary columns (page 125); formulas and continuation (page 223); running headers, section symbols and hyphenated line breaks. |
| Contents defect | Literal `???` references on PDF pages **3, 21, 22, 109, 235, 245**. Confirmed visually on page 3 and in content streams. Do not invent citation destinations. |
| Pagination | Printed page 19 on PDF page 1 through printed page 278 on PDF page 260; preserve both numbering systems. |
| Notices/provenance | PASS: original URL, checksum, archived approval, attribution, historical metadata and federal-work reuse notice match preserved records. `LicenseRef-US-Government-Work` retains third-party exceptions. |

No copyright marker was found by the limited literal-text scan, and no new
third-party restriction was observed in sampled pages. Permission-keyword hits
on pages 15 and 257 concern regulatory processes, not reuse grants. This is not
exhaustive rights clearance of all embedded objects. The GPO mark was visible;
its digital signature was not independently verified.

Future PDF processing must preserve reading order, table headings/cells/footnotes,
formulas, section hierarchy and citations; handle blank pages, headers and
hyphenation; and flag unresolved contents references. Review any newly surfaced
third-party notice. No processed text corpus or preprocessing module was created.
Thirteen temporary page renderings were used for inspection and removed.

## Synthetic HR

**Recommendation: APPROVE the content for a clearly labeled fictional public
demonstration, subject to owner approval of publication scope/rights.** Existing
`internal_demo` labels and rights metadata remain unchanged.

All five saved policies were read: `em-hr-leave-v1`, `em-hr-onboarding-v1`,
`em-hr-remote-work-v1`, `em-hr-attendance-v1`, `em-hr-offboarding-v1`.

- **Consistency: PASS.** Separate annual/sick allowances of 20/10 days, half-day
  rounding; 09:00-18:00 less a one-hour break gives 8 paid hours/day and 40/week.
  Approved leave excuses attendance/availability; remote work uses the same rules.
- **Workflows: PASS.** Role-based onboarding approval and least-privilege access;
  orientation within five business days and review after 30 calendar days.
  Offboarding has explicit notice/exception, final-date, handover, access revocation,
  asset-return and settlement steps. Access is not extended by late asset return.
- **Metadata/reproducibility: PASS.** Five unique IDs, all required fields, edition
  1.0.0 effective 2026-10-12. In-memory reproduction matches all five JSON files
  and their manifest, including template/generator/content/file hashes.
- **Privacy/labeling: PASS for these reviewed documents.** Roles only, no real
  employee information/contact values/credentials. Fictional banner,
  `is_fictional=true`, `project_authored_synthetic` and `internal_demo` are present.

Keep the fictional notice visible. These policies are demonstration rules, not
employment-law advice; classification metadata alone does not enforce access.
Future changes require a reviewed new edition.

## Six-domain inventory

| Domain | Source | Artifacts | Bytes | Preserved rights |
| --- | --- | ---: | ---: | --- |
| HR | EnterpriseMind synthetic v1 | 5 JSON | 21,918 | Original fictional material; publication decision pending |
| Technical | Python 3.12 tutorial index | 1 HTML | 35,271 | PSF-2.0 |
| IT | GNOME Network problems | 1 HTML | 10,674 | CC-BY-SA-3.0 |
| Finance | GovInfo FTR July 2025 | 1 PDF | 1,060,666 | Federal-work basis with exceptions |
| Product | LibreOffice Writer 25.2 preface | 1 HTML | 49,757 | CC-BY-4.0 |
| Support | Bitext v11 hybrid synthetic | 1 CSV; 26,872 records | 19,202,474 | CDLA-Sharing-1.0 |

**PASS:** six domains, ten document artifacts. Recomputed hashes, source URLs,
provenance, archived manifests and license/notice sidecars pass the existing
`prepare_distribution` checks in memory. Bitext matches the publisher pin.
See [full hashes/paths](../../data/README.md) and [licenses](../../data/LICENSES.md).

The public manifest still has five approved sources plus blocked, unapproved,
non-allowlisted GitLab; local HR has separate versioned provenance.
Canonical manifest hash:
`d60938ffbf55ed3dd25edde28771fdfd1576e10b7b9f1fc28b9d541446e7b621`.
All 28 runtime files, the source manifest and original roadmap retained identical
hashes, sizes and modification times. Index/preface sources remain bounded seeds.

## Original quality-review validation

Executed with the existing Python 3.12 environment:

```powershell
$env:PYTHONPATH = (Resolve-Path .\src).Path
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -B -m enterprise_mind.ingestion validate
.\.venv\Scripts\python.exe -B -m enterprise_mind.ingestion.synthetic_hr --check
git status --short --untracked-files=all
git diff --check
```

- **82 tests: 81 passed, one skipped** (host does not allow the existing real-symlink
  test). Manifest and synthetic HR validation: **PASS**.
- **Git safety: PASS.** All 28 runtime files ignored; none tracked; no tracked
  ignored files. Used NUL-delimited Git paths to avoid Windows stdin CRLF artifacts.
- `git diff --check`: **exit 0**, no whitespace errors; existing LF-to-CRLF warnings
  only. No line-ending configuration changed.
- **Only this report was added.** Earlier uncommitted EM-002 files remain.
  No original dataset, approval, code, template, security control or roadmap changed.

Do not commit raw/generated datasets, temporary renderings, `.venv/`, actual
environment/secrets files or private review extracts. This report has no contact
values. Code/templates, license resources and reviewed metadata/docs are expected
review candidates, not an instruction to stage everything.

**Outstanding:** implementation and verification of the mandatory Bitext and
LibreOffice exclusions/holds; public-demo/publication permission with applicable
license obligations; validated PDF extraction and preserved HR labels. These are
tracked as EM-002-F01 through EM-002-F05 in the [backlog](../project/backlog.md).
Privacy review was scoped to flagged patterns and complete HR documents, not an
exhaustive audit of unflagged public text.

The validation/change list above records the original quality-review step. The
[final commit/PR review](../project/em-002-pr.md) records the subsequent EM-002
finalization changes and rerun results. Neither collection approval nor successful
`prepare_distribution` verification grants indexing or publication permission.

**Technical collection: PASS. Indexing/public-demo sign-off: BLOCKED pending
review.** No downloads, installations, preprocessing pipeline, chunking, embeddings,
commits, pushes or merges occurred.
