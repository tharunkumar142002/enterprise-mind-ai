# Project backlog: EM-002 follow-up gates

Recorded 2026-10-12 for `feature/EM-002-data-collection`. These are local backlog
IDs, not externally created issues. All items below are **OPEN** and mandatory
before the affected later-stage work. Suggested owners are roles, not assignments.
The [original fourteen-stage roadmap](roadmap.md) remains unchanged.

**Collection approval permits controlled acquisition only.** The manifest's
`collection_for_rag` value does not authorize preprocessing, indexing, training,
publication or a public demonstration. No indexing or publication approval has
been granted. Public access classification, a verified license, a passing test or
a complete `prepare_distribution` bundle cannot substitute for that approval.

These gates are documented requirements for future implementation. EM-002 has no
indexer, privacy filter or publication service that enforces them. Until an
authorized follow-up implements and validates the relevant controls, keep the
affected documents out of indexing and hold public demonstration/publication.
Preserve raw artifacts; create any approved derivatives separately with their
own hashes, exclusion/change records and original-source provenance.

| Local ticket | Mandatory gate | Suggested owner | Blocks |
| --- | --- | --- | --- |
| EM-002-F01 | Bitext record exclusions and individual privacy clearance | Data engineering + privacy reviewer | Support indexing |
| EM-002-F02 | LibreOffice contact passage exclusion or whole-document hold | Data engineering + privacy reviewer | Product indexing |
| EM-002-F03 | Validated extraction of the 260-page historical finance PDF | Data engineering + domain reviewer | Finance preprocessing acceptance/indexing |
| EM-002-F04 | Preserve fictional HR labels and internal-demo classification | Data engineering + product owner | HR indexing/demo acceptance |
| EM-002-F05 | Separate use approvals, license obligations and publication permissions | Project owner + rights/privacy reviewer | All indexing, training and publication/public demo |

## EM-002-F01: Bitext exclusions

Source: `support-bitext-v11`. Snapshot SHA-256:
`6f81102b0100b97b8468eb04368033a23206bf1fde9d53500d5806ec1001a434`.
Exclude these **30 complete records** from future indexing until each is
individually cleared:

```text
18201, 21324, 21328, 21375, 21554, 21784, 21933, 21986, 21994, 22054,
22175, 22228, 22259, 22287, 22320, 22445, 22516, 22525, 22602, 22632,
22646, 22697, 22727, 22760, 22765, 22768, 22779, 22784, 22795, 22864
```

Locators are **1-based parsed CSV data-record ordinals excluding the header**, not
physical lines. Twenty-nine have uncertain email findings; record 18201 has an
uncertain phone finding despite its clearly synthetic email. Contact values must
not enter tickets, fixtures, reports or logs. See the
[privacy evidence](../data/final-data-quality-review.md#privacy-findings).

Acceptance criteria for the future implementation:

- Bind exclusions to the exact source ID and snapshot hash; fail closed for
  missing/mismatched snapshots or invalid locators instead of guessing row identity.
- Apply the exclusion before producing indexing inputs, chunks, embeddings,
  retrieval caches or public demo exports; test that all 30 are absent.
- Keep each record blocked until a reviewer records its individual disposition,
  evidence reference, reviewer role, date and permitted use without contact values.
  Do not treat publisher synthetic classification as individual privacy clearance.
- Preserve the original CSV. Record excluded ordinals/reasons and derived hashes;
  retain Bitext's hybrid-synthetic classification and CDLA-Sharing notices.
- Test boundary cases with fictional fixtures. Unflagged rows still require the
  general use/rights gate; this pattern review was not an exhaustive PII audit.

## EM-002-F02: LibreOffice contact passage

Source: `product-libreoffice-writer`. Snapshot SHA-256:
`690bdc861c56fb4a543624cb33c2f29a6d4cb4240e51983de0339899a1793371`.
The Feedback/documentation passage contains one public business email and a
matching `mailto:` link. Public business classification is not retrieval approval.

- Exclude the contact-routing passage and link from future indexing, or hold the
  **entire document** if a reliable passage locator/exclusion is unavailable.
- Verify the exclusion against this exact snapshot. Missing/changed locators must
  hold the document, not silently include it. Test both visible text and link targets.
- Preserve required copyright/contributor credits, CC-BY-4.0 terms, source URL and
  change notices in legal/provenance artifacts. Removing retrieval text does not
  authorize stripping legal attribution or changing the raw HTML.
- Record a reviewer-approved derivative and its checksum before lifting the hold.

## EM-002-F03: finance PDF extraction acceptance

Source: `finance-govinfo-ftr-2025`. Snapshot SHA-256:
`6ef76df3e84446a6413341aeaf7edc9c1da2ed3b127de31e7d8a190d12cf4f0c`.
This is the **260-page Subtitle F excerpt**, U.S. federal jurisdiction, edition
**2025-07-01**. It is historical reference, not current 2026 law or company policy.
See the [sampled visual review](../data/final-data-quality-review.md#finance-pdf).

- Obtain separate preprocessing authorization and validate an extractor before
  admitting its output to indexing. EM-002 implements no extraction pipeline.
- Account for all 260 PDF pages, including blank separators (observed on pages
  2 and 4), and preserve PDF-page versus printed-page references (19 through 278).
- Validate two-column reading order, full-width/multicolumn tables, headings,
  footnotes, formulas, section citations, hyphenation and continuation across pages.
  Include the reviewed difficult pages 44, 125 and 223 in acceptance fixtures.
- Preserve and flag literal `???` contents references observed on PDF pages
  3, 21, 22, 109, 235 and 245; never fabricate destinations or missing legal text.
- Record coverage/fidelity evidence and manual review of representative prose,
  tables and formulas; text operators alone are not successful extraction.
- Carry edition, jurisdiction, historical status, source hash and notices through
  derivatives. Review any additional third-party material surfaced by extraction.
  The sampled review did not certify every embedded object's rights or the PDF's
  digital signature.

## EM-002-F04: synthetic HR labeling

Applies to all five `hr-enterprisemind-synthetic-v1` policies, edition 1.0.0,
effective 2026-10-12, and their reproducible manifest.

- Preserve the fictional banner, `is_fictional=true`,
  `project_authored_synthetic`, `internal_demo`, source/document IDs and
  template/generator/content hashes through approved derivatives and citations.
- Make the fictional nature visible in any later demo interface; do not present
  these rules as a real employer's policies or legal advice. Do not silently
  relabel `internal_demo` as public. Metadata is not access-control enforcement.
- Test label/provenance propagation and fail on missing or contradictory labels.
  Keep shared policy rules consistent; changed content needs a reviewed new edition.
- Obtain owner approval of public-demo scope and rights separately under F05.
  The favorable content review recommendation is not publication authorization.

## EM-002-F05: rights and intended-use approval

Applies to every collected/generated artifact and any proposed derivative.

- Record separate decisions for collection, indexing, training and publication
  against the exact artifact/derived snapshot, audience, purpose and reviewer.
  An absent or pending decision must block the corresponding future action.
- Review preserved full terms, source-specific exceptions, privacy dispositions,
  attribution, modification notices and applicable CC share-alike/CDLA-Sharing
  obligations for the proposed use. Check Data/Enhanced Data/Results distinctions
  before Bitext export; do not infer blanket publication rights from its license.
- Retain complete terms, notices, original URLs and truthful transformation
  provenance. `prepare_distribution` verifies an in-memory bundle only; its
  success is neither indexing nor publication clearance.
- Decide licensing/public-demo permission for original HR templates and material.
  Third-party license resources do not license EnterpriseMind application code or
  original HR content. A public repository/PR itself also needs owner authorization.
- Keep `hr-gitlab-people` unapproved, non-allowlisted and blocked. Preserving its
  license bundle grants no collection or downstream permission.
- Before lifting a gate, record evidence and passing tests in the backlog and
  obtain the owner's applicable next-stage authorization. No gate closes merely
  because EM-002 is committed or merged.
