"""Prepare an offline distribution's complete file set without writing/publishing."""

import hashlib
import json
import re
from pathlib import Path
from typing import Any
from uuid import NAMESPACE_URL, uuid5

from enterprise_mind.ingestion.collector import CollectionError, safe_path
from enterprise_mind.ingestion.licensing import license_preservation
from enterprise_mind.ingestion.manifest import MAX_DOWNLOAD_BYTES, blocked_reasons, load_manifest


def _read(workspace: Path, path: Path, limit: int) -> bytes:
    with safe_path(workspace, path).open("rb") as stream:
        data = stream.read(limit + 1)
    if len(data) > limit:
        raise CollectionError("distribution artifact exceeds size limit")
    return data


def prepare_distribution(*, workspace: Path, record_path: Path) -> dict[str, bytes]:
    """Return unchanged document, LICENSE, NOTICE and provenance as one required set.

    No downloads, writes or publication. Exact reviewed source bindings are
    required. Collection approval is not publication approval.
    """
    try:
        workspace = workspace.resolve(strict=True)
        path = safe_path(workspace, record_path)
        record: dict[str, Any] = json.loads(_read(workspace, path, 1_048_576))
        output = path.parent.parent.parent
        manifest_hash = record["provenance"]["manifest_sha256"]
        if not isinstance(manifest_hash, str) or not re.fullmatch("[a-f0-9]{64}", manifest_hash):
            raise CollectionError("invalid archived manifest checksum")
        manifest_path = output / "manifests" / f"{manifest_hash}.json"
        safe_path(workspace, manifest_path)
        manifest = load_manifest(manifest_path)
        if (manifest.sha256 != manifest_hash
                or hashlib.sha256(_read(workspace, manifest_path, 1_048_576)).hexdigest()
                != manifest_hash):
            raise CollectionError("archived manifest checksum mismatch")
        source = next((item for item in manifest.sources
                       if item.source_id == record["source_id"]), None)
        if source is None or blocked_reasons(source, manifest):
            raise CollectionError("record lacks an approved, allowlisted collection snapshot")
        expected = license_preservation(source.source_id, source.url, source.license,
                                        file_format=source.format, category=source.category)
        if expected is None:
            raise CollectionError("distribution requires a reviewed local license bundle")
        for key in ("license", "notices"):
            artifact_path = output / "licenses" / f"{expected[key]['sha256']}.txt"
            expected[key]["path"] = artifact_path.relative_to(workspace).as_posix()
        if record.get("license_preservation") != expected:
            raise CollectionError("missing or altered preserved license/attribution")
        if ("source_metadata" in expected
                and record["provenance"].get("source_metadata") != expected["source_metadata"]):
            raise CollectionError("source-specific provenance mismatch")
        if any(record["provenance"].get(key) != value
               for key, value in source.provenance.items()):
            raise CollectionError("publisher/classification provenance mismatch")
        if (record["source_url"] != source.url or record["license"] != source.license
                or record["format"] != source.format or source.format not in {"html", "pdf", "csv"}
                or record["category"] != source.category or record["title"] != source.title
                or record["source_version"] != source.version
                or record["access_classification"] != "public"
                or record["provenance"]["original_source_url"] != source.url
                or record["provenance"]["license_attribution"] != source.license["attribution"]
                or record["provenance"]["approval"] != source.approval
                or record["provenance"]["verification"] != source.verification):
            raise CollectionError("source/license provenance mismatch")
        notices = {}
        for key in ("license", "notices"):
            artifact = expected[key]
            data = _read(workspace, Path(artifact["path"]), 65_536)
            if data != artifact["text"].encode("utf-8"):
                raise CollectionError("license/notice artifact failed integrity checks")
            notices[key] = data
        digest = record["checksum"]["value"]
        if (record["checksum"]["algorithm"] != "sha256" or not isinstance(digest, str)
                or not re.fullmatch("[a-f0-9]{64}", digest)):
            raise CollectionError("invalid document checksum")
        document_id = str(uuid5(NAMESPACE_URL, f"{source.url}#sha256={digest}"))
        if record["version"] != f"sha256:{digest}":
            raise CollectionError("document version/checksum mismatch")
        blob = output / "blobs" / digest
        if (record["blob_path"] != blob.relative_to(workspace).as_posix()
                or record["document_id"] != document_id
                or path != output / "records" / source.source_id /
                f"{document_id}-{manifest_hash[:16]}.json"):
            raise CollectionError("document identity/path mismatch")
        document = _read(workspace, blob, min(source.max_bytes, MAX_DOWNLOAD_BYTES))
        if (not document or hashlib.sha256(document).hexdigest() != digest
                or len(document) != record["size_bytes"]
                or source.expected_sha256 not in (None, digest)):
            raise CollectionError("document failed integrity checks")
        notice = (notices["notices"] + (
            f"\nAttribution: {expected['attribution']}\n"
            f"Original source URL: {source.url}\n"
            f"Changes: {expected['changes']}\n"
        ).encode("utf-8"))
        return {f"document.{source.format}": document, "LICENSE.txt": notices["license"],
                "NOTICE.txt": notice,
                "provenance.json": (json.dumps(record, ensure_ascii=False, indent=2)
                                    + "\n").encode("utf-8")}
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        raise CollectionError(f"cannot prepare licensed distribution: {exc}") from exc
