"""Strict schema-1 collection records shared by collection and distribution.

Only integer schema_version 1 is supported. The original schema allows omission
of license_preservation for sources without bundled terms, and source_metadata
for bindings without additional context. Distribution still requires terms.
No legacy, partial or future schemas are inferred or migrated.
"""

import json
import re
from datetime import datetime
from typing import Any
from uuid import NAMESPACE_URL, uuid5

from enterprise_mind.ingestion.manifest import (
    CATEGORIES,
    FORMAT_MIME_TYPES,
    MAX_DOWNLOAD_BYTES,
    Manifest,
    validate_unicode,
)

MAX_RECORD_BYTES = 1_048_576
_FIELDS = frozenset({
    "schema_version", "document_id", "source_id", "source_url", "title", "category",
    "format", "collected_at", "license", "checksum", "version", "source_version",
    "access_classification", "provenance", "size_bytes", "blob_path", "transfer",
})
_PROVENANCE_FIELDS = frozenset({
    "kind", "publisher", "notes", "verification", "approval", "manifest_sha256",
    "original_source_url", "license_attribution",
})
_TIMESTAMP = re.compile(
    r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}"
    r"(?:\.[0-9]{1,6})?(?:Z|[+-](?:[01][0-9]|2[0-3]):[0-5][0-9])\Z"
)
_HASH = re.compile(r"[a-f0-9]{64}\Z")


class ProvenanceError(ValueError):
    """A collection record cannot be trusted as schema-1 provenance."""


def _object(value: Any, required: frozenset[str], *,
            optional: frozenset[str] = frozenset()) -> dict[str, Any]:
    if (not isinstance(value, dict) or not required <= value.keys()
            or value.keys() - required - optional):
        raise ProvenanceError("record has missing or unsupported metadata fields")
    return value


def _text(value: Any) -> None:
    if not isinstance(value, str) or not value.strip() or len(value) > 4096:
        raise ProvenanceError("record metadata must contain nonblank bounded text")


def validate_record(value: Any, manifest: Manifest | None = None) -> dict[str, Any]:
    """Validate shape/types, timestamps and identity; optionally bind to a manifest."""
    validate_unicode(value)
    record = _object(value, _FIELDS, optional=frozenset({"license_preservation"}))
    if type(record["schema_version"]) is not int or record["schema_version"] != 1:
        raise ProvenanceError("record schema_version must be integer 1")
    timestamp = record["collected_at"]
    if not isinstance(timestamp, str) or not _TIMESTAMP.fullmatch(timestamp):
        raise ProvenanceError("collected_at must be a timezone-aware RFC 3339 timestamp")
    try:
        parsed = datetime.fromisoformat(timestamp)
        if parsed.utcoffset() is None:
            raise ValueError("missing timezone")
    except ValueError as exc:
        raise ProvenanceError("invalid collected_at timestamp") from exc
    for field in ("source_id", "source_url", "title", "source_version", "blob_path"):
        _text(record[field])
    if (not re.fullmatch(r"[a-z][a-z0-9_-]{2,47}", record["source_id"])
            or not isinstance(record["category"], str) or record["category"] not in CATEGORIES
            or not isinstance(record["format"], str) or record["format"] not in FORMAT_MIME_TYPES
            or record["access_classification"] != "public"):
        raise ProvenanceError("invalid record source identity/classification")
    if type(record["size_bytes"]) is not int or not 1 <= record["size_bytes"] <= MAX_DOWNLOAD_BYTES:
        raise ProvenanceError("invalid record size_bytes")
    checksum = _object(record["checksum"], frozenset({"algorithm", "value"}))
    digest = checksum["value"]
    if (checksum["algorithm"] != "sha256" or not isinstance(digest, str)
            or not _HASH.fullmatch(digest)):
        raise ProvenanceError("invalid record checksum")
    if (record["version"] != f"sha256:{digest}"
            or record["document_id"] != str(uuid5(
                NAMESPACE_URL, f"{record['source_url']}#sha256={digest}"))):
        raise ProvenanceError("record document identity/checksum mismatch")
    transfer = record["transfer"]
    if not isinstance(transfer, dict) or transfer.keys() - {"etag", "last-modified"}:
        raise ProvenanceError("invalid transfer metadata")
    for item in transfer.values():
        if (not isinstance(item, str) or len(item) > 8192
                or any(ord(char) < 32 or ord(char) == 127 for char in item)):
            raise ProvenanceError("invalid transfer validator")
    _object(record["license"], frozenset({
        "name", "identifier", "url", "status", "attribution", "notes",
    }))
    provenance = _object(record["provenance"], _PROVENANCE_FIELDS,
                         optional=frozenset({"source_metadata"}))
    for field in ("kind", "publisher", "notes", "original_source_url", "license_attribution"):
        _text(provenance[field])
    manifest_hash = provenance["manifest_sha256"]
    if not isinstance(manifest_hash, str) or not _HASH.fullmatch(manifest_hash):
        raise ProvenanceError("invalid archived manifest checksum")
    _object(provenance["verification"], frozenset({
        "status", "checked_on", "evidence_urls", "notes",
    }))
    _object(provenance["approval"], frozenset({
        "approved", "approved_by", "approved_at", "allowed_uses",
    }))
    for parent, key in ((record, "license_preservation"), (provenance, "source_metadata")):
        if key in parent and not isinstance(parent[key], dict):
            raise ProvenanceError(f"invalid {key} metadata")
    preservation = record.get("license_preservation", {})
    if (("source_metadata" in provenance) != ("source_metadata" in preservation)
            or json.dumps(provenance.get("source_metadata"), sort_keys=True)
            != json.dumps(preservation.get("source_metadata"), sort_keys=True)):
        raise ProvenanceError("source-specific provenance does not match preserved metadata")
    if manifest is not None:
        source = next((item for item in manifest.sources
                       if item.source_id == record["source_id"]), None)
        if source is None or manifest.sha256 != manifest_hash:
            raise ProvenanceError("record does not match the archived manifest")
        expected = {
            "source_url": source.url, "title": source.title, "category": source.category,
            "format": source.format, "source_version": source.version,
            "access_classification": source.access_classification, "license": source.license,
            "provenance": {**source.provenance, "verification": source.verification,
                           "approval": source.approval, "manifest_sha256": manifest.sha256,
                           "original_source_url": source.url,
                           "license_attribution": source.license["attribution"]},
        }
        actual = {key: record[key] for key in expected}
        actual["provenance"] = {key: item for key, item in provenance.items()
                                if key != "source_metadata"}
        # JSON comparison distinguishes booleans from integers in nested metadata.
        if json.dumps(actual, sort_keys=True) != json.dumps(expected, sort_keys=True):
            raise ProvenanceError("record source/provenance differs from the archived manifest")
        if (record["size_bytes"] > source.max_bytes
                or source.expected_sha256 not in (None, digest)):
            raise ProvenanceError("record violates the source size/checksum constraint")
    return record


def _unique_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ProvenanceError("duplicate record JSON key")
        result[key] = value
    return result


def _invalid_constant(value: str) -> None:
    raise ProvenanceError("non-JSON number in record")


def load_record(raw: bytes) -> dict[str, Any]:
    """Reject oversized, ambiguous or malformed record JSON before use."""
    if len(raw) > MAX_RECORD_BYTES:
        raise ProvenanceError("record exceeds size limit")
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_keys,
                           parse_constant=_invalid_constant)
        return validate_record(value)
    except (ValueError, RecursionError) as exc:
        raise ProvenanceError(f"invalid provenance record: {exc}") from exc
