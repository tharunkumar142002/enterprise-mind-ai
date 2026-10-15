"""Prepare an offline distribution's complete file set without writing/publishing."""

import hashlib
import json
from pathlib import Path

from enterprise_mind.ingestion.collector import CollectionError, safe_path
from enterprise_mind.ingestion.licensing import license_preservation
from enterprise_mind.ingestion.manifest import MAX_DOWNLOAD_BYTES, blocked_reasons, load_manifest
from enterprise_mind.ingestion.provenance import MAX_RECORD_BYTES, load_record, validate_record


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
        record = load_record(_read(workspace, path, MAX_RECORD_BYTES))
        output = path.parent.parent.parent
        manifest_hash = record["provenance"]["manifest_sha256"]
        manifest_path = output / "manifests" / f"{manifest_hash}.json"
        safe_path(workspace, manifest_path)
        manifest = load_manifest(manifest_path)
        if (manifest.sha256 != manifest_hash
                or hashlib.sha256(_read(workspace, manifest_path, 1_048_576)).hexdigest()
                != manifest_hash):
            raise CollectionError("archived manifest checksum mismatch")
        validate_record(record, manifest)
        source = next((item for item in manifest.sources
                       if item.source_id == record["source_id"]), None)
        if (source is None or blocked_reasons(source, manifest)
                or source.format not in {"html", "pdf", "csv"}):
            raise CollectionError("record lacks an approved, allowlisted collection snapshot")
        expected = license_preservation(source.source_id, source.url, source.license,
                                        file_format=source.format, category=source.category)
        if expected is None:
            raise CollectionError("distribution requires a reviewed local license bundle")
        for key in ("license", "notices"):
            artifact_path = output / "licenses" / f"{expected[key]['sha256']}.txt"
            expected[key]["path"] = artifact_path.relative_to(workspace).as_posix()
        if (json.dumps(record.get("license_preservation"), sort_keys=True)
                != json.dumps(expected, sort_keys=True)):
            raise CollectionError("missing or altered preserved license/attribution")
        if ("source_metadata" in expected
                and record["provenance"].get("source_metadata") != expected["source_metadata"]):
            raise CollectionError("source-specific provenance mismatch")
        notices = {}
        for key in ("license", "notices"):
            artifact = expected[key]
            data = _read(workspace, Path(artifact["path"]), 65_536)
            if data != artifact["text"].encode("utf-8"):
                raise CollectionError("license/notice artifact failed integrity checks")
            notices[key] = data
        digest = record["checksum"]["value"]
        document_id = record["document_id"]
        blob = output / "blobs" / digest
        if (record["blob_path"] != blob.relative_to(workspace).as_posix()
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
