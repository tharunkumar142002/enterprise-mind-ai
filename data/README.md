# EM-002 dataset inventory and offline verification

Verified locally on 2026-10-12. Six active category sources supply **10 document
artifacts**: five collected public-source files and five original fictional HR
policies. The Bitext CSV is one artifact containing **26,872 data rows**.
These are seed datasets; this count does not imply complete handbooks or tutorials.

**Collection validation passes; indexing and public demonstration remain blocked.**
The [final quality review](../docs/data/final-data-quality-review.md) supersedes the
initial screening dispositions below. Follow the
[mandatory backlog gates](../docs/project/backlog.md): exclude the 30 flagged
Bitext records until individually cleared; exclude the LibreOffice contact passage
or hold the whole document; require validated extraction of the 260-page finance
PDF; preserve fictional HR labels; and obtain separate rights/use permission.
`collection_for_rag` approval alone does not authorize indexing or publication.

## Six-category inventory

| Category | Source ID | Resource / edition | Artifacts | Document bytes | Rights / license |
| --- | --- | --- | --- | --- | --- |
| HR | `hr-enterprisemind-synthetic-v1` | EnterpriseMind Demo Company (fictional), v1.0.0, effective 2026-10-12 | 5 JSON records with Markdown content | 21,918 | Original project demonstration material; external license/publication decision pending owner review |
| Technical | `technical-python-tutorial` | [Python 3.12 tutorial index](https://docs.python.org/3.12/tutorial/index.html) | 1 HTML | 35,271 | PSF-2.0 |
| IT | `it-gnome-network` | [GNOME Network problems](https://help.gnome.org/gnome-help/net-problem.html) | 1 HTML | 10,674 | CC-BY-SA-3.0 |
| Finance | `finance-govinfo-ftr-2025` | [GovInfo FTR, July 2025](https://www.govinfo.gov/content/pkg/CFR-2025-title41-vol4/pdf/CFR-2025-title41-vol4-subtitleF.pdf) | 1 PDF | 1,060,666 | LicenseRef-US-Government-Work |
| Product | `product-libreoffice-writer` | [LibreOffice Writer Guide 25.2 preface](https://books.libreoffice.org/en/WG252/WG2500-Preface.html) | 1 HTML | 49,757 | CC-BY-4.0 |
| Customer support | `support-bitext-v11` | [Bitext v11](https://raw.githubusercontent.com/bitext/customer-support-llm-chatbot-training-dataset/main/data/Bitext_Sample_Customer_Support_Training_Dataset_27K_responses-v11.csv) | 1 CSV | 19,202,474 | CDLA-Sharing-1.0 |

The five public sources were collected on 2026-10-11 and remain unchanged.
Their total document size is **20,358,842 bytes**; including HR document records,
the total is **20,380,760 bytes**, excluding manifests and license/provenance
sidecars. The HR manifest is another **2,085 bytes**. No new downloads were made.

The public download manifest remains [sources.yaml](sources.yaml), unchanged by
the HR task. It has six public candidates, of which five are approved.
`hr-gitlab-people` remains an **unapproved, blocked candidate**, absent from the
allowlist and this active inventory. Local synthetic HR is defined by its own
[versioned template](../src/enterprise_mind/ingestion/templates/hr-v1.json);
it does not add a fake URL or weaken the public-only collector schema.

## Public-source integrity and locations

Every listed SHA-256 was recalculated from the saved blob and matched its record.
Blobs are stored at `data/raw/blobs/<sha256>`, without a filename extension.
Each linked record supplies the original URL, stable document ID, title, category,
UTC collection time, source/content versions, public access classification, license,
attribution, archived manifest hash and exact artifact paths.

| Source | Blob SHA-256 | Immutable provenance |
| --- | --- | --- |
| `technical-python-tutorial` | `b4523c8c3f4876d5cb5ce67489916a816b67bdae62f651709aa115303af3381e` | [Record](raw/records/technical-python-tutorial/640eee1c-466a-5481-9534-3c4c6ea36680-37eed17b209ba5d9.json) |
| `it-gnome-network` | `1620e8036df9d268e5015d332f01c27ef9c56595d0b98ef2986d6495bb1689d9` | [Record](raw/records/it-gnome-network/721ec5ce-fb4a-5234-a8f4-c4a8b22e6442-d60938ffbf55ed3d.json) |
| `finance-govinfo-ftr-2025` | `6ef76df3e84446a6413341aeaf7edc9c1da2ed3b127de31e7d8a190d12cf4f0c` | [Record](raw/records/finance-govinfo-ftr-2025/9404fdf3-0a03-5bdc-87ea-bf815973cf6b-d60938ffbf55ed3d.json) |
| `product-libreoffice-writer` | `690bdc861c56fb4a543624cb33c2f29a6d4cb4240e51983de0339899a1793371` | [Record](raw/records/product-libreoffice-writer/4bc10913-a4c4-52d9-9106-75c7d249a8ba-d60938ffbf55ed3d.json) |
| `support-bitext-v11` | `6f81102b0100b97b8468eb04368033a23206bf1fde9d53500d5806ec1001a434` | [Record](raw/records/support-bitext-v11/c37d4ec2-818c-5519-80dd-d20974dda378-d60938ffbf55ed3d.json) |

All five sources passed the existing offline `prepare_distribution` validation:
source/approval/allowlist snapshot, document identity, size/checksum, pinned local
license/notice bindings, embedded terms, preserved sidecars and source-specific
provenance. The helper prepared file sets in memory only; nothing was exported.
Bitext additionally matches its pinned publisher SHA-256 exactly.

There are **22 existing raw files**: five blobs, five provenance records, ten
license/notice sidecars and two archived manifests, totaling **20,536,588 bytes**.
All their bytes and the existing public manifest were preserved during this task.
The Python record intentionally references its original earlier manifest snapshot.
No GitLab record or unexpected sixth downloaded source is present.

## Synthetic HR artifacts and provenance

Generated under ignored `data/synthetic/hr/v1/`, with a [manifest](synthetic/hr/v1/manifest.json).
Each JSON contains title, ID, category `human_resources`, version `1.0.0`,
effective date `2026-10-12`, owner `People Operations (fictional)`,
access classification `internal_demo`, `is_fictional=true`, Markdown content,
content SHA-256, referenced shared policy values and synthetic provenance.

| Document ID | JSON bytes | File SHA-256 |
| --- | --- | --- |
| `em-hr-attendance-v1` | 3,740 | `a4ede12614a44d61b46ef1452e3873fccbf45539c104ff4c81dfce4b93084c79` |
| `em-hr-leave-v1` | 4,753 | `896378dbe425d95c99e9f2289ec89a4b6edbe5556c37d05e728e60a8c21845b9` |
| `em-hr-offboarding-v1` | 4,501 | `bd5f0adcbd19491bd07b22bd9a50332341fea97b1dd8f688cde76ab8c702ad45` |
| `em-hr-onboarding-v1` | 4,945 | `92e49fd44559e7c0e39c46fce3b426ce695e9275ac045d8138ec5fecf92946f9` |
| `em-hr-remote-work-v1` | 3,979 | `151ab8424a5e4f649ba312b594ac60381643f99a3d6279c08266ed47946c10b2` |

The provenance classification is `project_authored_synthetic`, with an explicit
Codex-assisted authoring statement and human review pending. Original source URL
is null because these are local original templates. Canonical template hash and
normalized generator hash identify the exact source materials. No wall-clock
timestamp, randomness or runtime model output changes reproducible bytes.

See [generation, validation and policy rules](../docs/data/synthetic-hr.md).
These records contain roles and workflows, not employee records. The access
classification is demonstration metadata; access enforcement is a future stage.

## Content suitability and review findings

All five public artifacts are intact inputs for a later **reviewed** preprocessing
step. Collection integrity does not establish privacy clearance, legal clearance
for every derivative use, full format conformance or readiness to index directly.

| Source | Read-only inspection | Review required before indexing / distribution |
| --- | --- | --- |
| Python | UTF-8 HTML parses; title identifies Python 3.12.15; 173 links, 11 script elements; no email-pattern matches in visible text | Tutorial index only. Strip navigation/scripts in a later approved step; do not crawl chapter links without approval. Preserve full PSF terms and notices. |
| GNOME | UTF-8 HTML parses; title Network problems; 75 links, 3 script elements; no email-pattern matches in visible text | Index/short summaries only. No linked troubleshooting articles were collected. Retain author credit and CC-BY-SA terms; review share-alike handling of adapted extracts. |
| Finance | PDF signature and final EOF marker valid; size, checksum and historical source metadata pass | Full text, page layout and third-party notice review remains pending: no PDF extraction tool was available and none was installed. U.S. federal July 1, 2025 edition, **not current 2026 law**, Indian law or company policy. |
| LibreOffice | UTF-8 HTML parses; Preface title; 83 links, 2 script elements; **one email-like match** in visible text | Review contact-bearing passages for exclusion/redaction in future derived text. Keep contributor attribution in preserved notices; review public names/credits separately from retrieval content. Preface/FAQs only, not the full guide. |
| Bitext | Strict UTF-8 CSV parsing: 26,872 rows, 11 categories, 27 intents; no malformed rows, no blank instruction/category/intent/response, no exact duplicate rows | **55 rows with email-like text, one with phone-like text**, and 13,041 rows with double-brace placeholders. Manual review must distinguish examples/placeholders from real contact data and decide exclusions. Do not index as real tickets or authoritative EnterpriseMind policy. |
| Fictional HR | Five records pass exact template/metadata validation, unique IDs, shared-rule consistency, contact/credential exclusion checks and byte-reproducibility tests | Owner review of demonstration policies remains pending; any changes require a new reviewed edition. No claim of real employment-law compliance or blanket external publication rights. |

Pattern counts are screening findings, not confirmed real PII counts or proof of
PII absence. Values were not copied into this inventory, logs or test fixtures.
No raw files were redacted or otherwise changed. Bitext's publisher describes
hybrid synthetic data using natural seeds; it is distinct from project-authored HR.
Its CDLA-Sharing obligations and source provenance remain attached.

## Validation and boundaries

- Complete suite: **82 tests executed, 81 passed, one skipped**, on Python 3.12.10.
  The skip is the existing test requiring host permission to create a symlink.
- Eighteen new offline tests cover HR metadata, IDs, classification, reproducible
  output, policy conflicts, contact/credential exclusion and immutable safe paths.
- Existing HTTPS, redirect rejection, approval, allowlist, caps, license,
  checksum and provenance controls remain intact.
- Runtime raw and synthetic files remain Git-ignored and outside container contexts.
  The original 14-stage roadmap is unchanged.
- No dependency installation, download, chunking, embeddings, commit, push or merge
  is part of this HR increment.

The [license index](LICENSES.md) and [source review](../docs/data/source-readiness.md)
remain required context for later processing. Future preprocessing/publication
requires the owner's next instruction and resolution of the applicable findings.
