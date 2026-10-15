"""Exact source bindings for reviewed local terms; no network or approval effects."""

import hashlib
from importlib.resources import files
from typing import Any

from enterprise_mind.ingestion.reviewed_sources import REVIEWED_SOURCES

PYTHON_SOURCE_ID = "technical-python-tutorial"
PYTHON_SOURCE_URL = "https://docs.python.org/3.12/tutorial/index.html"
PYTHON_LICENSE_URL = "https://docs.python.org/3.12/license.html"
MAX_LICENSE_BYTES = 65_536
# Pins for the already reviewed resources, normalized only for checkout newlines.
PYTHON_RESOURCE_HASHES = {
    "PSF-2.0.txt": "0b480bdaffca0d14ae4225a69758e104ba01ed1abd92676f1516d23c75357c81",
    "python-copyright.txt": "92c355dc9e24bc0e5fbfbdbd1d30f5ffebc68a78b5f2cd956ee2eccdcc36a764",
}


def _reviewed_resource(filename: str, expected_sha256: str) -> dict[str, str]:
    """Bound reads before hashing; preserve the reviewed text and newline policy."""
    resource = files("enterprise_mind.ingestion").joinpath("licenses").joinpath(filename)
    with resource.open("r", encoding="utf-8") as stream:
        text = stream.read(MAX_LICENSE_BYTES + 1)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    encoded = text.encode("utf-8")
    if not text.strip() or len(encoded) > MAX_LICENSE_BYTES:
        raise ValueError("bundled license/notice resource is empty or too large")
    digest = hashlib.sha256(encoded).hexdigest()
    if digest != expected_sha256:
        raise ValueError("bundled terms/notices do not match the reviewed full text")
    return {"text": text, "sha256": digest}


def license_preservation(
    source_id: str, source_url: str, license_data: dict[str, Any],
    *, file_format: str | None = None, category: str | None = None,
) -> dict[str, Any] | None:
    """Bind terms to exact reviewed resources, never to arbitrary license claims."""
    if source_id != PYTHON_SOURCE_ID and source_url != PYTHON_SOURCE_URL:
        return _enterprise_preservation(source_id, source_url, license_data,
                                        file_format, category)
    if (source_id != PYTHON_SOURCE_ID or source_url != PYTHON_SOURCE_URL
            or license_data.get("identifier") != "PSF-2.0"
            or license_data.get("url") != PYTHON_LICENSE_URL
            or license_data.get("status") != "verified"):
        raise ValueError("Python source does not match the reviewed license binding")
    if (file_format not in (None, "html")
            or category not in (None, "technical_documentation")):
        raise ValueError("Python format/category does not match the reviewed binding")
    attribution = license_data.get("attribution")
    if not isinstance(attribution, str) or not attribution.strip():
        raise ValueError("license attribution is required")
    result: dict[str, Any] = {
        "identifier": "PSF-2.0", "original_source_url": source_url,
        "license_url": PYTHON_LICENSE_URL,
        "copyright_url": "https://docs.python.org/3.12/copyright.html",
        "reviewed_on": "2026-10-11", "attribution": attribution,
        "changes": "None: original downloaded bytes preserved without modification.",
    }
    for key, filename in (("license", "PSF-2.0.txt"), ("notices", "python-copyright.txt")):
        result[key] = _reviewed_resource(filename, PYTHON_RESOURCE_HASHES[filename])
    return result


def _enterprise_preservation(
    source_id: str, source_url: str, license_data: dict[str, Any],
    file_format: str | None, category: str | None,
) -> dict[str, Any] | None:
    binding = REVIEWED_SOURCES.get(source_id)
    if binding is None:
        if any(item["url"] == source_url for item in REVIEWED_SOURCES.values()):
            raise ValueError("reviewed URL does not match its source ID")
        return None
    if (source_url != binding["url"] or license_data.get("status") != "verified"
            or license_data.get("identifier") != binding["identifier"]
            or license_data.get("url") != binding["license_url"]
            or file_format not in (None, binding["format"])
            or category not in (None, binding["category"])):
        raise ValueError("source does not match the reviewed license binding")
    attribution = license_data.get("attribution")
    if not isinstance(attribution, str) or not attribution.strip():
        raise ValueError("license attribution is required")
    result = {
        "identifier": binding["identifier"], "original_source_url": source_url,
        "license_url": binding["license_url"],
        "copyright_url": binding["copyright_url"],
        "reviewed_on": "2026-10-11", "attribution": attribution,
        "changes": "None: original downloaded bytes preserved without modification.",
        "source_metadata": dict(binding["source_metadata"]),
    }
    for key in ("license", "notices"):
        result[key] = _reviewed_resource(binding[key + "_file"], binding[key + "_sha256"])
    return result
