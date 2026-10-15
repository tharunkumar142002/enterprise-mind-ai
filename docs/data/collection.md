# EM-002: enterprise source collection, first increment

## Current status

The [source manifest](../../data/sources.yaml) contains six public candidates.
Python, GNOME, GovInfo, LibreOffice and Bitext were explicitly approved and then
collected under separate owner execution authorization on 2026-10-11. All five
passed offline artifact, provenance and license verification on 2026-10-12.
GitLab remains unapproved, absent from the allowlist and blocked by privacy review.
The HR task preserves the manifest and all existing raw artifacts without downloads.
The [six-category inventory](../../data/README.md) also includes five locally
generated fictional HR policies. See [synthetic HR usage](synthetic-hr.md).
Local synthetic generation uses its own versioned templates and never bypasses
this collector's public-source approval or exact-URL rules.

Collection approval is scoped to acquisition under `collection_for_rag`; it does
not authorize preprocessing, indexing, training or publication. The
[final quality review](final-data-quality-review.md) and
[mandatory backlog gates](../project/backlog.md) govern subsequent work: exclude
the 30 flagged Bitext records until individually cleared; exclude LibreOffice's
contact passage or hold its whole document; validate extraction of the 260-page
historical finance PDF; preserve HR fictional/internal-demo labels; and obtain
separate use/rights approval. These are requirements for future implementation,
not an existing privacy filter or indexing authorization. See
[source evidence](source-readiness.md).

The module uses only Python 3.12's standard library. Tests are synthetic and
network-free. Use an existing working Python 3.12 interpreter for the commands
below. Interpreter availability can differ between the IDE and agent sessions;
no package installation or environment repair is part of EM-002.

## Source inventory and pending reviews

| Source ID / domain | Resource | License evidence and remaining work |
| --- | --- | --- |
| `hr-gitlab-people` / HR | [GitLab People Group](https://handbook.gitlab.com/handbook/people-group/) HTML seed | [Publisher states CC-BY-SA-4.0](https://handbook.gitlab.com/handbook/about/handbook-usage/). Review selected content, PII, exclusions and attribution/share-alike before approval. |
| `it-gnome-network` / IT | [GNOME Network problems](https://help.gnome.org/gnome-help/net-problem.html) HTML seed | Exact upstream page explicitly includes CC-BY-SA-3.0 legal.xml and credits The Ubuntu Documentation Team; verified, terms/notices bundled. Replaces unavailable Ubuntu URL. |
| `finance-govinfo-ftr-2025` / Finance | [GovInfo FTR July 2025](https://www.govinfo.gov/content/pkg/CFR-2025-title41-vol4/pdf/CFR-2025-title41-vol4-subtitleF.pdf) PDF | U.S. federal regulatory text reuse basis, with third-party exceptions; notices bundled. MODS dateIssued 2025-07-01; historical reference, not current 2026 law. |
| `product-libreoffice-writer` / Product | [Writer Guide 25.2 preface/FAQs](https://books.libreoffice.org/en/WG252/WG2500-Preface.html) HTML | Select verified CC-BY-4.0 from publisher alternatives; full terms, 2025 copyright and contributor credits bundled. Software licenses and trademarks are separate. |
| `support-bitext-v11` / Support | [Official Bitext repository](https://github.com/bitext/customer-support-llm-chatbot-training-dataset), direct GitHub CSV in manifest | Verified CDLA-Sharing-1.0; full terms/sharing notices bundled. Hybrid synthetic origin retained. Direct URL has no redirect; 20 MiB per-source cap. |
| `technical-python-tutorial` / Technical | [Python 3.12 tutorial index](https://docs.python.org/3.12/tutorial/index.html) HTML | Already collected and verified; unchanged in this task. Existing PSF terms, copyright sidecars and archived approval remain intact. Do not select it for the new batch. |

The Bitext file-information page, not the raw file, supplied its actual CSV URL,
published SHA-256 and approximate 19.2 MB size. Those facts are recorded in the
manifest. The downloaded bytes now match that publisher SHA-256, recalculated
locally. Any future acquisition must still pass the existing checksum pin;
the mutable `main` URL is not itself immutable. Its per-source cap remains
20 MiB (20,971,520 bytes); explicitly
use that reviewed global cap for this source. Other sources retain 5 MiB limits.

These are bounded seed resources; the collector does not crawl links, query APIs,
extract archives or acquire complete handbooks. Seed indexes need individually
researched/approved chapter URLs to expand the corpus. Five fictional HR policies
now supply local enterprise workflow content; additional fictional domains/tickets
remain future work under [the dataset plan](dataset-plan.md).

## Manifest format and validation

`sources.yaml` deliberately uses JSON syntax, a subset of YAML 1.2. This avoids
adding a YAML dependency. The loader rejects ordinary YAML mappings, tags, anchors,
duplicate JSON keys, non-JSON numbers, invalid UTF-8 and manifests over 1 MiB.
Keep the JSON syntax when editing; unsupported syntax fails with a clear error.

Top-level fields are `schema_version` (integer 1), `manifest_id`, `researched_on`,
`allowlisted_urls` (exact URLs, not hosts/globs) and `sources` (1-100 records).
Every source must contain:

| Field | Meaning |
| --- | --- |
| `source_id`, `name`, `title` | Unique safe identifier, publisher/source label and selected document title |
| `url`, `category`, `format` | Exact HTTPS resource, one of the six normalized domains and supported format |
| `version`, `expected_sha256` | Publisher revision/alias and optional lowercase content pin; never invent a revision/hash |
| `access_classification`, `max_bytes` | `public` only in this increment; source byte cap no higher than 32 MiB |
| `license` | Name, nullable identifier/evidence URL, `verified` or `pending_review`, attribution and caveats |
| `verification` | `pending_review`, `research_verified` or final `verified`; evidence URLs, review date and notes |
| `approval` | Boolean approval, reviewer, timezone-aware approval timestamp and approved use |
| `provenance` | `public_document` or `public_synthetic_dataset`, publisher and origin notes |

Unknown/missing fields, invalid values, duplicate IDs/resource URLs/allowlist entries
and unknown allowlisted URLs are rejected. Source IDs are lowercase safe names,
3-48 characters; reserved Windows device names are forbidden. Formats are `txt`,
`md`, `html`, `pdf`, `csv`, `json`, `jsonl`. Formats describe raw resources; this
increment does not parse, chunk or embed their contents.

The manifest records evidence; it does not perform legal judgment or establish
cryptographic reviewer identity. An approved manifest is trusted, reviewed project
configuration. Only an authorized reviewer may change approval/allowlist fields.

## Supported collection-record schema

Collection reuse and distribution preparation accept only integer
`schema_version: 1`. Records must contain `document_id`, `source_id`, `source_url`,
`title`, `category`, `format`, `collected_at`, `license`, `checksum`, `version`,
`source_version`, `access_classification`, `provenance`, `size_bytes`, `blob_path`
and `transfer`. Unknown fields, duplicate JSON keys, non-JSON numbers, malformed
Unicode and records over 1 MiB fail closed. `collected_at` must be a valid RFC 3339
timestamp with a timezone, seconds and at most six fractional digits. Existing
valid timestamps and transfer validators are retained on repeat collection.

The original schema-1 variants remain supported: `license_preservation` may be
absent for sources without bundled terms; `provenance.source_metadata` is present
for bindings with additional reviewed context. Distribution requires a complete
reviewed license bundle. Mandatory provenance fields are `kind`, `publisher`,
`notes`, `verification`, `approval`, `manifest_sha256`, `original_source_url` and
`license_attribution`. Metadata is checked against the archived manifest and the
reviewed license binding. No other schema version or incomplete legacy record is
accepted or automatically migrated. Existing downloaded artifacts are not rewritten.

## Offline usage

Run from the repository root with an existing working Python 3.12 interpreter:

```powershell
$env:PYTHONPATH = (Resolve-Path .\src).Path
.\.venv\Scripts\python.exe -B -m enterprise_mind.ingestion validate
.\.venv\Scripts\python.exe -B -m enterprise_mind.ingestion collect --source technical-python-tutorial
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -v
```

Use a working `python` command in place of the `.venv` path if Python 3.12 is
already available. Do not install or rebuild the environment as a side effect.
The `validate` command prints source count, manifest fingerprint and block reasons.
`collect` without `--download` returns a plan and performs no network calls or
output writes, even for approved sources. Repeating `--source` selects a bounded
batch; duplicate/unknown selections fail. There is no automatic collect-all mode.

The `enterprise-mind-collect` console entry point is declared for a future approved
package installation; it is not installed in this increment. Exit codes: 0 for
valid metadata/plans/success, 2 for invalid arguments, policy rejection or failure.

## Review before execution

1. Review actual source content, document-specific rights/exclusions, attribution,
   privacy, public access and exact endpoint behavior. Do not infer rights from
   public availability or a broad software license.
2. Resolve pending license findings and document them in `license.notes`. Set
   license/source statuses to `verified` only after the applicable checks pass.
3. Obtain user approval for the named resource and `collection_for_rag` use.
   Record the real reviewer and timestamp; add only its exact URL to the allowlist.
   This approval does not grant indexing, training or publication permission.
4. After authorization, execution additionally requires the explicit `--download`
   flag. Existing acquisition is complete; the HR increment makes no requests.

All five approved sources are already collected. Do not execute another collection
as part of the HR task. Historical commands are retained in
[source-readiness.md](source-readiness.md); their presence does not authorize a
new download. GitLab remains blocked. Future acquisition needs new task scope.

The entire selection passes policy preflight before directories or requests are
created. The module never edits approval fields. License evidence URLs are stored
as metadata, not automatically downloaded. All six known sources have reviewed
local resources; collection never makes a second request for terms or notices.

## Python license and attribution preservation

The reviewed binding is limited to `technical-python-tutorial`, its exact index
URL, license identifier `PSF-2.0`, and the official license evidence URL. A changed
binding or unavailable local resource fails before network calls or output writes.
This mechanism neither approves sources nor changes the allowlist. The five new
bindings in `reviewed_sources.py` additionally require their exact ID, URL, license
identifier/evidence URL, format and category. Full terms and project-authored notice
summaries are pinned by normalized UTF-8 SHA-256; modified, missing, empty or over
64 KiB resources fail before network calls or writes. Terms are unmodified legal
texts; summaries do not replace them. GovInfo uses an explicitly local reuse-basis
identifier and notice, rather than claiming a publisher SPDX license.
The Python PSF license and copyright resources use the same bounded-read, 64 KiB
limit and pinned-hash checks. Only checkout newline normalization is permitted;
the bundled legal texts are unchanged.

The package includes the full eight-clause [PSF License Version 2 text](../../src/enterprise_mind/ingestion/licenses/PSF-2.0.txt)
and [copyright notices](../../src/enterprise_mind/ingestion/licenses/python-copyright.txt),
reviewed on 2026-10-11 against the official pages above. Preserve the original
2001-2023 PSF notice, the current 2001-2026 footer notice and the other listed
copyright holders. PSF-2.0 is the selected license for both prose and code examples;
the optional code-only 0BSD alternative does not relicense the prose. Review any
additional notices in the actual selected snapshot before authorizing collection.
These third-party resources do not relicense EnterpriseMind's own application code.

After an authorized successful collection, the record embeds the full license and
notices in `license_preservation`, their SHA-256 hashes, attribution, evidence URLs,
review date, original document URL and an unchanged-bytes change statement.
Immutable text sidecars are written under `data/raw/licenses/<sha256>.txt`.
Provenance also explicitly includes `original_source_url` and `license_attribution`.
Existing corrupted sidecars fail rather than being overwritten. Repeated identical
collection retains the original record and reuses identical sidecars.

Later distribution preparation uses this offline Python API:

```python
from pathlib import Path
from enterprise_mind.ingestion.distribution import prepare_distribution

# Replace this path with a real record only after separately authorized collection.
file_set = prepare_distribution(
    workspace=Path.cwd(),
    record_path=Path("data/raw/records/technical-python-tutorial/<actual-record>.json"),
)
# Required complete set: document.html, LICENSE.txt, NOTICE.txt, provenance.json.
```

The helper returns the complete in-memory file set. It performs no downloads,
writes, archive creation or publication. Keep all four files together in any later
archive/export: `LICENSE.txt` contains the full terms, and `NOTICE.txt` includes
copyright holders, original URL, attribution and change summary. The helper checks
the archived approved/allowlisted manifest, source provenance, document checksum,
embedded license/notice bundle and both on-disk text sidecars. Missing or altered
artifacts, paths outside `data/raw`, unsupported sources and older records without
preserved terms fail closed. It does not migrate old records or fetch missing terms.

Unchanged raw HTML, PDF and CSV from reviewed bindings are supported, with
`document.html`, `document.pdf` or `document.csv` in the complete four-file set.
Full terms/notices are bounded at 64 KiB each; the original 16 KiB bound could not
carry the complete CC legal texts. Source-specific metadata is checked in both the
preserved bundle and provenance: finance dates/jurisdiction/historical status,
GNOME author/license inclusion, LibreOffice version and Bitext synthetic origin.
Publisher/classification, title, category, version and checksum integrity are also
checked before preparation. Existing Python preservation metadata remains identical.
Future extracted, chunked or modified
documents must carry their own truthful change summary and preserve the same
license/notice evidence; that transformation work is outside this increment.
Preparing files does not authorize indexing or publication: collection approval
is scoped to acquisition under `collection_for_rag`. The helper may return raw
content subject to privacy holds; do not export it merely because integrity checks
pass. Distribution needs separate rights/privacy review and owner authorization
under [EM-002-F05](../project/backlog.md#em-002-f05-rights-and-intended-use-approval).

## Safety and reproducibility

- HTTPS only, port 443, DNS hostnames, no embedded credentials, query strings or
  fragments. Exact URL matching; no proxy inheritance, cookies or authentication.
- Resolve once, reject private/loopback/link-local/multicast destinations, pin the
  public IP for the connection and validate TLS against the original hostname.
  Redirects and non-200 responses fail; no hidden retries or CDN fallback.
- Default request/body budget is 15 seconds (`--timeout-seconds`, maximum 60).
  DNS caller waiting is bounded using a daemon worker; OS resolver work can persist
  briefly after a timeout. The watchdog records expiration and interrupts sockets
  during headers and body reads. Deadlines are checked after each read (including
  EOF/final bytes), after transport cleanup and before artifact publication.
- The HTTPS transport supports only a single decimal `Content-Length` frame.
  Conflicting/duplicate/malformed framing headers, all `Transfer-Encoding`
  values (including chunked), malformed parsed headers and lengthless HTTP 200
  responses are rejected. This deliberately excludes connection-close framing,
  whose early EOF cannot prove a complete document. A later framing extension
  requires its own complete-body validation and regression tests. Injected test
  transports provide complete in-memory bodies; they must report incomplete
  bodies as errors rather than clean EOF.
- Default global size cap is 5 MiB (`--max-bytes`, maximum 32 MiB). Apply the lower
  of global/source caps, checking both declared length and streamed bytes. Reject
  empty/truncated transfers, MIME mismatches and compressed bodies.
- Writes stay under the current workspace's `data/raw/`, including any custom
  `--output`. Reject traversal, symlinks, Windows junctions and non-regular files.
  Filename/title/Content-Disposition never controls output paths. The local
  workspace must be trusted against concurrent malicious filesystem mutation.
- An exclusive output lock prevents concurrent collectors. Atomic hard-link
  publication never replaces existing blobs/records; partial staging files are
  removed on ordinary errors. Filesystem hard-link support is required.
- SHA-256 content-addressed blobs are shared for duplicates. Each distinct source
  retains its own stable URL/content-derived document ID and provenance record.
  Repeated identical collection preserves original metadata/timestamp. The result
  reports `duplicate_content` and `already_collected` where applicable.
- Optional expected SHA-256 pins reject changed bytes before publication. Live
  aliases cannot promise identical future bytes without a pin. Record the publisher
  version and the actual checksum-derived content version separately.
- Archive the canonical manifest and its SHA-256 fingerprint. Metadata includes
  source URL/ID, title, domain/format, UTC timestamp, full license/evidence/approval
  snapshot, checksum/version, access classification, size and transfer validators.
  All six reviewed sources embed the preserved terms and notice artifact paths.

Existing ignored runtime layout (preserved unchanged by the HR task):

```text
data/raw/
├── manifests/<manifest-sha256>.json
├── blobs/<content-sha256>
├── licenses/<license-or-notice-sha256>.txt  # Python terms and notices
├── records/<source-id>/<document-id>-<manifest-fingerprint-prefix>.json
└── .staging/                         # Temporary files; cleaned on handled errors
```

The existing `.gitignore` excludes these files and `data/synthetic/`. Reviewed
`data/sources.yaml`, `data/README.md` and `data/LICENSES.md` are explicit exceptions.
Container contexts exclude all `data/`.
There is no claim that raw HTML is sanitized or safe to render/execute.

## Failure and recovery

Downloads are atomic per artifact, not an all-or-nothing transaction across a
batch. On failure, prior successful sources remain; an interrupted publication
can leave an unreferenced blob/manifest. Rerunning an authorized selection checks
blob integrity and reuses identical content. Never overwrite corrupted artifacts
to hide a failure. Hard process termination may leave a lock/staging file: inspect
for a running collector before a separately authorized cleanup. No automatic
destructive cleanup is performed.

Synthetic tests cover manifest failures, approval/allowlist boundaries, limits,
MIME/redirect rejection, deadlines, checksum pins, duplicate content, safe paths,
private DNS answers, immutable records and lock handling. Symlink tests skip when
the host disallows link creation. Run live endpoint verification only in a later
authorized download task; no network-dependent integration test is run here.
License tests additionally cover complete terms/notices, attribution/provenance,
sidecar reuse and corruption, fail-closed distribution preparation, missing local
resources and unchanged approval/no-network boundaries.
