# EM-002 selected source readiness

Original source review date: 2026-10-11. Subsequent owner authorization allowed
collection of the four selected sources on that date. All five existing sources,
including Python, passed offline integrity/license validation on 2026-10-12.
See the [current inventory and content-review findings](../../data/README.md).
The [final quality review](final-data-quality-review.md) records subsequent privacy
and PDF findings. Its [mandatory follow-up gates](../project/backlog.md) supersede
the pending-review descriptions in this historical source-selection inventory.
Collection approval does not authorize indexing or publication; both remain held
for separate review and implementation of the applicable gates.
The owner explicitly approved `it-gnome-network`,
`finance-govinfo-ftr-2025`, `product-libreoffice-writer` and `support-bitext-v11`
for controlled local `collection_for_rag`; their exact URLs are now allowlisted.
Approval was recorded at 2026-10-11T15:23:07+00:00 after offline verification of
their exact URL/format/category/license bindings and pinned full terms/notices.
GitLab remains unapproved and absent from the allowlist. The original Python source object and all
existing raw artifacts are unchanged. The fourteen-stage roadmap is unchanged.

## Inventory and evidence

| Source ID | Exact selected URL | Terms / notices | Header size and format | Readiness |
| --- | --- | --- | --- | --- |
| `hr-gitlab-people` | https://handbook.gitlab.com/handbook/people-group/ | CC-BY-SA-4.0; GitLab contributors | 2,384,068 bytes; HTML; HTTP 200 | License verified; privacy decision blocks source verification and collection |
| `it-gnome-network` | https://help.gnome.org/gnome-help/net-problem.html | CC-BY-SA-3.0; The Ubuntu Documentation Team | 10,674 bytes; HTML; HTTP 200 | Collected; checksum and license/provenance verified |
| `finance-govinfo-ftr-2025` | https://www.govinfo.gov/content/pkg/CFR-2025-title41-vol4/pdf/CFR-2025-title41-vol4-subtitleF.pdf | Federal regulatory text; 17 U.S.C. 105; third-party exceptions | 1,060,666 bytes; PDF; HTTP 200 | Collected as historical reference; text/layout review pending |
| `product-libreoffice-writer` | https://books.libreoffice.org/en/WG252/WG2500-Preface.html | CC-BY-4.0 selected from publisher alternatives; team copyright and contributors | 49,757 bytes; HTML; HTTP 200 | Collected; contact-bearing content review pending |
| `support-bitext-v11` | https://raw.githubusercontent.com/bitext/customer-support-llm-chatbot-training-dataset/main/data/Bitext_Sample_Customer_Support_Training_Dataset_27K_responses-v11.csv | CDLA-Sharing-1.0; Bitext Innovations; publisher hybrid synthetic | 19,202,474 bytes; CSV served as text/plain; HTTP 200 | Collected within 20 MiB cap; publisher checksum matches; contact-like text review pending |

The HTTP entries above are historical header observations, not a guarantee of
future GET behavior. Redirects were not followed. The collected byte counts match
those reviewed sizes; payload hashes are in the current inventory. No endpoints
were fetched again for the HR increment. The default cap remains 5 MiB and hard
maximum 32 MiB. Bitext's source cap remains 20 MiB; it was not increased.

GNOME's official mirror [page source](https://github.com/GNOME/gnome-user-docs/blob/master/gnome-help/C/net-problem.page)
was verified through the [GitHub source metadata API](https://api.github.com/repos/GNOME/gnome-user-docs/contents/gnome-help/C/net-problem.page).
Its page ID/title match this resource, it credits The Ubuntu Documentation Team,
and explicitly XIncludes [legal.xml](https://github.com/GNOME/gnome-user-docs/blob/master/gnome-help/C/legal.xml),
which specifies CC-BY-SA-3.0. The source Git blob is
`a914344cedb8d8628a22d52fb4745575de8f7cb4`; this is evidence, not a downloaded
HTML checksum. The earlier exact-page licensing gap is resolved. This page is an
index; related troubleshooting articles require their own review and approval.

GovInfo's [official MODS](https://www.govinfo.gov/metadata/pkg/CFR-2025-title41-vol4/mods.xml)
has dateIssued `2025-07-01` and preferred citation "Code of Federal Regulations
Title 41, Volume 4, July 1, 2025". Record that publication metadata date as the
edition/revision date. Do not infer the actual release date or individual rule
effective dates. Jurisdiction is **United States federal**; `historical_reference`
is true and `current_law_claim` false. This is not current 2026 law, Indian law or
a fictional company policy. [GovInfo reuse policy](https://www.govinfo.gov/about/policies)
provides the federal-work basis, with exceptions for protected third-party items.
`LicenseRef-US-Government-Work` is an explicit project-local identifier. Unexpected
third-party notices must be reviewed before later extraction or distribution.

[LibreOffice's copyright section](https://books.libreoffice.org/en/WG252/WG2500-Preface.html)
permits GPL version 3 or later OR CC Attribution version 4.0 or later. Select
CC-BY-4.0, retain the 2025 team copyright and all listed contributor credits, source,
license and modification notices. The document was published February 2025 for
version 25.2; no exact day is invented. Trademarks/software licenses remain separate.

Bitext's [official publisher license](https://github.com/bitext/customer-support-llm-chatbot-training-dataset/blob/main/LICENSE.txt)
matches CDLA-Sharing-1.0. Retain provider credits, notices, metadata and source
links. Published Data/Enhanced Data remain under the unmodified agreement;
changes need prominent notices and further restrictions cannot be imposed. The
Results exception permits only de minimis source data, not unrestricted RAG
quotation. The [publisher card](https://huggingface.co/datasets/bitext/Bitext-customer-support-llm-chatbot-training-dataset)
describes hybrid synthetic examples using natural seeds; these are neither real
tickets nor project-authored fictional records. Inspect unexpected PII/third-party
material after authorized acquisition before indexing. Provider representations
are not an independent audit. Preserve the publisher checksum
`6f81102b0100b97b8468eb04368033a23206bf1fde9d53500d5806ec1001a434`;
GitHub mirror byte identity passed at collection and again in the offline audit.
A future mismatch must fail;
do not remove the pin to make collection succeed. The `main` URL is mutable.

## GitLab privacy review

The [public People Group body](https://handbook.gitlab.com/handbook/people-group/)
contains reusable HR workflow descriptions, but also identifiable routing data.
The [publisher license](https://handbook.gitlab.com/handbook/about/handbook-usage/)
confirms CC-BY-SA-4.0; licensing does not remove the project's privacy requirement.

Flag the following for exclusion/redaction without copying their personal values
into this report, source control, fixtures or logs:

- Individual handles in the contact-routing table and any named personnel or
  employee-profile links, including navigation that is outside the HR body.
- Email/phone/fax contact details and contact-routing identifiers. Some are group
  or public service contacts rather than personal data; exclude them from the demo
  corpus anyway because they could trigger real-company contact workflows.
- Internal handbook, Slack, Workday, Compass, survey, calendar and issue destinations.
  Never follow them or acquire confidential employee/complaint records.
- Complaint-reporting/investigation passages require context review; they describe
  workflows, not permission to collect reports or impersonate GitLab staff.

Retain generic People Operations responsibilities, response timelines and HR
workflow knowledge only after a reviewed processing decision. The current collector
preserves raw bytes and does not redact. Therefore GitLab remains `pending_review`,
unapproved and absent from the allowlist. This task implements no sanitization,
chunking or embeddings and makes no claim that the raw page is PII-free.

The current HR category instead uses original project-authored fictional policies.
See [synthetic HR](synthetic-hr.md). This does not approve GitLab or resolve its blocker.

## License preservation and distribution

Four full official license texts were preserved locally, plus a clearly labeled
GovInfo reuse-basis notice and five source-specific attribution summaries. Exact
bindings pin source ID, URL, format, category, license identifier/evidence URL and
SHA-256 of the normalized UTF-8 terms and notices. Summaries are project-authored
and do not replace full terms or invent copyright dates. The package-data glob
already includes these resources; no dependency change is needed.

Collection uses no extra network requests for licenses. It writes immutable,
content-addressed sidecars and embeds terms/notices, attribution, source URL and
source-specific metadata in the record. Distribution preparation requires the
archived approved/allowlisted manifest, original blob, checksum and matching terms,
notices and provenance. HTML/PDF/CSV export sets must keep document, LICENSE,
NOTICE and provenance together. Missing/corrupt assets fail closed. Publication
and training are outside collection approval.

## Offline validation and historical collection commands

Currently safe to run: offline validation and dry runs. The four approved sources
report eligible; GitLab reports incomplete review, missing approval and no allowlist.
Eligibility does not execute collection: the CLI defaults to a no-network dry run.

```powershell
$env:PYTHONPATH = (Resolve-Path .\src).Path
.\.venv\Scripts\python.exe -B -m enterprise_mind.ingestion validate --manifest data/sources.yaml
.\.venv\Scripts\python.exe -B -m enterprise_mind.ingestion collect --manifest data/sources.yaml --source it-gnome-network --source finance-govinfo-ftr-2025 --source product-libreoffice-writer --output data/raw --timeout-seconds 15 --max-bytes 5242880
.\.venv\Scripts\python.exe -B -m enterprise_mind.ingestion collect --manifest data/sources.yaml --source support-bitext-v11 --output data/raw --timeout-seconds 60 --max-bytes 20971520
```

The following download commands record the **already completed acquisition** after
separate owner authorization. They are not instructions to repeat collection in
the HR task:

```powershell
.\.venv\Scripts\python.exe -B -m enterprise_mind.ingestion collect --manifest data/sources.yaml --source it-gnome-network --source finance-govinfo-ftr-2025 --source product-libreoffice-writer --output data/raw --timeout-seconds 15 --max-bytes 5242880 --download
.\.venv\Scripts\python.exe -B -m enterprise_mind.ingestion collect --manifest data/sources.yaml --source support-bitext-v11 --output data/raw --timeout-seconds 60 --max-bytes 20971520 --download
```

All four downloads succeeded and their artifacts remain intact. Do not redownload
them without a new instruction. GitLab is deliberately excluded until its privacy
blocker is resolved. Python was excluded because it was already collected.
The Bitext-specific longer budget remains
within the existing 60-second maximum; other controls are unchanged. Batches are
atomic per artifact, not across sources; inspect results after a failure.
