# Dataset license and attribution index

This index points to the source-specific terms already preserved by EM-002.
It does not replace those full texts or grant publication/training permission.
No licensing evidence was fetched or changed in the synthetic HR task.

| Source | Preserved terms | Preserved source notices | Handling for later derivatives / exports |
| --- | --- | --- | --- |
| Python tutorial | [PSF-2.0](../src/enterprise_mind/ingestion/licenses/PSF-2.0.txt) | [Python copyright](../src/enterprise_mind/ingestion/licenses/python-copyright.txt) | Keep applicable terms, copyright, source attribution and truthful change notices. |
| GNOME Network problems | [CC-BY-SA-3.0](../src/enterprise_mind/ingestion/licenses/CC-BY-SA-3.0.txt) | [GNOME notices](../src/enterprise_mind/ingestion/licenses/gnome-notices.txt) | Preserve The Ubuntu Documentation Team credit, source/license links and adaptation notices; review share-alike obligations for derivatives. |
| GovInfo FTR July 2025 | [Federal-work reuse basis](../src/enterprise_mind/ingestion/licenses/US-Government-Work.txt) | [GovInfo notices](../src/enterprise_mind/ingestion/licenses/govinfo-notices.txt) | Project-local `LicenseRef-US-Government-Work`; do not assume third-party inclusions share this basis. Preserve U.S. federal jurisdiction and historical edition/date. |
| LibreOffice Writer preface | [CC-BY-4.0](../src/enterprise_mind/ingestion/licenses/CC-BY-4.0.txt) | [LibreOffice notices](../src/enterprise_mind/ingestion/licenses/libreoffice-notices.txt) | Selected publisher option; keep team copyright, contributor credits, source/license and modification notices. Trademarks/software licenses are separate. |
| Bitext v11 | [CDLA-Sharing-1.0](../src/enterprise_mind/ingestion/licenses/CDLA-Sharing-1.0.txt) | [Bitext notices](../src/enterprise_mind/ingestion/licenses/bitext-notices.txt) | Preserve provider credit and unmodified agreement for distributed Data/Enhanced Data, applicable notices and change statements; no additional restrictions. Review the agreement's Results distinction before output distribution. |
| EnterpriseMind synthetic HR v1 | Original project-authored fictional policy templates | Authoring method, source kind, code/template hashes and review status embedded in every record | Local `collection_for_rag` demonstration use requested by the owner. External license/publication decision remains pending owner review; no invented SPDX license or imported third-party grant. |

The five public sources passed an offline license-preservation audit on 2026-10-12.
Immutable runtime copies are under `data/raw/licenses/`; their exact paths and
checksums are in the [provenance records](README.md). Required later public-source
export sets keep original document, LICENSE, NOTICE and provenance together.
The existing `prepare_distribution` helper validates and returns this complete
set in memory; it performs no publication and supports no HR export yet.

GitLab's preserved CC-BY-SA-4.0 license resources do **not** authorize collecting
GitLab: privacy review still blocks that candidate and it is not allowlisted.
The source manifest/approval statuses are unchanged. Third-party dataset licenses
do not license this application's code or the separately authored HR records.

The [content findings](README.md#content-suitability-and-review-findings), especially
contact-like text, publisher synthetic seed origin and unreviewed PDF inclusions,
must be resolved as appropriate before future indexing or distribution. Retain
mandatory legal credits in provenance/notices when deciding which personal names
or contact-bearing passages to exclude from retrieval text.
