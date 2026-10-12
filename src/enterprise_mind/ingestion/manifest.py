"""Strict, dependency-free source manifest validation.

The .yaml manifest uses JSON syntax, a YAML 1.2 subset. General YAML, aliases,
tags and implicit type conversion are intentionally unsupported.
"""

import hashlib
import ipaddress
import json
import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit

CATEGORIES = frozenset({
    "human_resources", "it_support", "finance", "product_documentation",
    "customer_support", "technical_documentation",
})
FORMAT_MIME_TYPES = {
    "txt": frozenset({"text/plain"}),
    "md": frozenset({"text/plain", "text/markdown"}),
    "html": frozenset({"text/html", "application/xhtml+xml"}),
    "pdf": frozenset({"application/pdf"}),
    "csv": frozenset({"text/csv", "application/csv", "text/plain"}),
    "json": frozenset({"application/json", "text/json"}),
    "jsonl": frozenset({"application/jsonl", "application/x-ndjson", "text/plain"}),
}
MAX_MANIFEST_BYTES = 1_048_576
MAX_DOWNLOAD_BYTES = 32 * 1024 * 1024
_ID = re.compile(r"[a-z][a-z0-9_-]{2,47}\Z")
_HASH = re.compile(r"[a-f0-9]{64}\Z")
_HOST = re.compile(r"(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+"
                   r"[a-zA-Z][a-zA-Z0-9-]{0,62}\Z")
_RESERVED = {"con", "prn", "aux", "nul", *(f"com{i}" for i in range(1, 10)),
             *(f"lpt{i}" for i in range(1, 10))}


class ManifestError(ValueError):
    """Manifest cannot be safely interpreted."""


def https_url(value: Any, label: str) -> str:
    """Require credential-free HTTPS DNS URLs; no local hosts or signed queries."""
    if not isinstance(value, str) or not value or len(value) > 2048:
        raise ManifestError(f"{label}: expected an HTTPS URL of at most 2048 characters")
    if any(char.isspace() or ord(char) < 32 or ord(char) == 127 for char in value):
        raise ManifestError(f"{label}: URL contains whitespace/control characters")
    try:
        parsed = urlsplit(value)
        host, port = parsed.hostname, parsed.port
    except ValueError as exc:
        raise ManifestError(f"{label}: invalid URL") from exc
    if (parsed.scheme != "https" or not host or not _HOST.fullmatch(host)
            or port not in (None, 443) or parsed.username is not None
            or parsed.password is not None or parsed.fragment or parsed.query
            or "\\" in unquote(value)):
        raise ManifestError(
            f"{label}: require HTTPS/443 and DNS hostname, no credentials/query/fragment"
        )
    if any(ord(char) < 32 or ord(char) == 127 for char in unquote(value)):
        raise ManifestError(f"{label}: encoded control characters are forbidden")
    try:
        ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        raise ManifestError(f"{label}: IP literals are forbidden")
    if host.endswith((".localhost", ".local", ".internal")):
        raise ManifestError(f"{label}: local/internal hosts are forbidden")
    return value


def _object(value: Any, required: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != required:
        raise ManifestError(f"{label}: fields must be exactly {', '.join(sorted(required))}")
    return value


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 4096:
        raise ManifestError(f"{label}: expected nonblank text (maximum 4096 characters)")
    return value


def _date(value: Any, label: str) -> str:
    value = _text(value, label)
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise ManifestError(f"{label}: expected ISO date") from exc
    return value


@dataclass(frozen=True)
class Source:
    source_id: str
    name: str
    title: str
    url: str
    category: str
    format: str
    version: str
    access_classification: str
    expected_sha256: str | None
    max_bytes: int
    license: dict[str, Any]
    verification: dict[str, Any]
    approval: dict[str, Any]
    provenance: dict[str, Any]


@dataclass(frozen=True)
class Manifest:
    sources: tuple[Source, ...]
    allowlisted_urls: frozenset[str]
    sha256: str
    canonical_json: bytes


def validate_manifest(value: Any) -> Manifest:
    """Reject unknown/missing fields, ambiguous types and unsafe identifiers."""
    root = _object(value, {"schema_version", "manifest_id", "researched_on",
                           "allowlisted_urls", "sources"}, "manifest")
    if type(root["schema_version"]) is not int or root["schema_version"] != 1:
        raise ManifestError("schema_version must be integer 1")
    _text(root["manifest_id"], "manifest_id")
    _date(root["researched_on"], "researched_on")
    if not isinstance(root["allowlisted_urls"], list):
        raise ManifestError("allowlisted_urls must be a list")
    urls = [https_url(url, "allowlisted_urls") for url in root["allowlisted_urls"]]
    if len(set(urls)) != len(urls):
        raise ManifestError("duplicate allowlisted URL")
    if not isinstance(root["sources"], list) or not 1 <= len(root["sources"]) <= 100:
        raise ManifestError("sources must contain 1-100 records")
    sources: list[Source] = []
    seen_ids: set[str] = set()
    seen_urls: set[str] = set()
    for index, raw in enumerate(root["sources"]):
        label = f"sources[{index}]"
        source = _object(raw, set(Source.__dataclass_fields__), label)
        source_id = _text(source["source_id"], f"{label}.source_id")
        if not _ID.fullmatch(source_id) or source_id in _RESERVED:
            raise ManifestError(f"{label}: unsafe source_id")
        if source_id in seen_ids:
            raise ManifestError(f"duplicate source_id: {source_id}")
        seen_ids.add(source_id)
        url = https_url(source["url"], f"{label}.url")
        if url in seen_urls:
            raise ManifestError(f"duplicate source URL: {url}")
        seen_urls.add(url)
        for field in ("name", "title", "version"):
            _text(source[field], f"{label}.{field}")
        if not isinstance(source["category"], str) or source["category"] not in CATEGORIES:
            raise ManifestError(f"{label}: unsupported category")
        if not isinstance(source["format"], str) or source["format"] not in FORMAT_MIME_TYPES:
            raise ManifestError(f"{label}: unsupported file format")
        if source["access_classification"] != "public":
            raise ManifestError(f"{label}: only public sources are permitted in EM-002")
        checksum = source["expected_sha256"]
        if checksum is not None and (
                not isinstance(checksum, str) or not _HASH.fullmatch(checksum)):
            raise ManifestError(f"{label}: expected_sha256 must be null or lowercase SHA-256")
        if (type(source["max_bytes"]) is not int
                or not 1 <= source["max_bytes"] <= MAX_DOWNLOAD_BYTES):
            raise ManifestError(f"{label}: max_bytes must be 1-{MAX_DOWNLOAD_BYTES}")
        license_data = _object(source["license"], {"name", "identifier", "url", "status",
                                                 "attribution", "notes"}, f"{label}.license")
        for field in ("name", "attribution", "notes"):
            _text(license_data[field], f"{label}.license.{field}")
        if license_data["identifier"] is not None:
            _text(license_data["identifier"], f"{label}.license.identifier")
        if license_data["url"] is not None:
            https_url(license_data["url"], f"{label}.license.url")
        if license_data["status"] not in ("verified", "pending_review"):
            raise ManifestError(f"{label}: unsupported license status")
        if license_data["status"] == "verified" and license_data["url"] is None:
            raise ManifestError(f"{label}: verified license needs evidence URL")
        verification = _object(source["verification"], {"status", "checked_on", "evidence_urls",
                                                       "notes"}, f"{label}.verification")
        if verification["status"] not in ("research_verified", "pending_review", "verified"):
            raise ManifestError(f"{label}: unsupported verification status")
        _date(verification["checked_on"], f"{label}.verification.checked_on")
        _text(verification["notes"], f"{label}.verification.notes")
        evidence = verification["evidence_urls"]
        if not isinstance(evidence, list) or not evidence:
            raise ManifestError(f"{label}: verification requires evidence_urls")
        for item in evidence:
            https_url(item, f"{label}.verification.evidence_urls")
        approval = _object(source["approval"], {"approved", "approved_by", "approved_at",
                                               "allowed_uses"}, f"{label}.approval")
        if type(approval["approved"]) is not bool:
            raise ManifestError(f"{label}: approval.approved must be a boolean")
        if not isinstance(approval["allowed_uses"], list) or any(
                use != "collection_for_rag" for use in approval["allowed_uses"]):
            raise ManifestError(f"{label}: only collection_for_rag use is supported")
        if approval["approved"]:
            _text(approval["approved_by"], f"{label}.approval.approved_by")
            try:
                approved_at = datetime.fromisoformat(approval["approved_at"])
                if approved_at.tzinfo is None:
                    raise ValueError("missing timezone")
            except (TypeError, ValueError) as exc:
                raise ManifestError(
                    f"{label}: approved_at needs a timezone-aware ISO timestamp"
                ) from exc
            if (approval["allowed_uses"] != ["collection_for_rag"]
                    or license_data["status"] != "verified"
                    or verification["status"] != "verified"):
                raise ManifestError(
                    f"{label}: approval needs verified source/license and collection_for_rag"
                )
        elif (approval["approved_by"] is not None or approval["approved_at"] is not None
              or approval["allowed_uses"]):
            raise ManifestError(f"{label}: unapproved sources cannot have approval metadata")
        provenance = _object(source["provenance"], {"kind", "publisher", "notes"},
                             f"{label}.provenance")
        if provenance["kind"] not in ("public_document", "public_synthetic_dataset"):
            raise ManifestError(f"{label}: unsupported provenance kind")
        _text(provenance["publisher"], f"{label}.provenance.publisher")
        _text(provenance["notes"], f"{label}.provenance.notes")
        sources.append(Source(**source))
    if set(urls) - seen_urls:
        raise ManifestError("allowlist contains a URL not present in sources")
    canonical = json.dumps(root, sort_keys=True, ensure_ascii=False, allow_nan=False,
                           separators=(",", ":")).encode("utf-8")
    # Own all mutable nested mappings; callers cannot change the input after validation.
    sources = [Source(**json.loads(json.dumps(source.__dict__))) for source in sources]
    return Manifest(tuple(sources), frozenset(urls),
                    hashlib.sha256(canonical).hexdigest(), canonical)


def _unique_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ManifestError(f"duplicate JSON object key: {key}")
        result[key] = value
    return result


def _invalid_constant(value: str) -> None:
    raise ManifestError(f"non-JSON number: {value}")


def load_manifest(path: Path) -> Manifest:
    """Bound manifest reads and reject YAML outside the documented JSON subset."""
    try:
        with path.open("rb") as stream:
            raw = stream.read(MAX_MANIFEST_BYTES + 1)
        if len(raw) > MAX_MANIFEST_BYTES:
            raise ManifestError("manifest exceeds 1 MiB")
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_keys,
                           parse_constant=_invalid_constant)
    except (OSError, UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ManifestError(f"cannot read JSON-formatted YAML manifest: {exc}") from exc
    return validate_manifest(value)


def blocked_reasons(source: Source, manifest: Manifest) -> list[str]:
    reasons = []
    if source.license["status"] != "verified":
        reasons.append("license pending review")
    if source.verification["status"] != "verified":
        reasons.append("document/endpoint review incomplete")
    if source.approval["approved"] is not True:
        reasons.append("explicit approval missing")
    if source.url not in manifest.allowlisted_urls:
        reasons.append("exact URL not allowlisted")
    return reasons
