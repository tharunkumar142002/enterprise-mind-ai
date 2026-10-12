"""Exact source bindings for reviewed local terms; no network or approval effects."""

import hashlib
from importlib.resources import files
from typing import Any

from enterprise_mind.ingestion.reviewed_sources import REVIEWED_SOURCES

PYTHON_SOURCE_ID = "technical-python-tutorial"
PYTHON_SOURCE_URL = "https://docs.python.org/3.12/tutorial/index.html"
PYTHON_LICENSE_URL = "https://docs.python.org/3.12/license.html"


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
    assets = files("enterprise_mind.ingestion").joinpath("licenses")
    result: dict[str, Any] = {
        "identifier": "PSF-2.0", "original_source_url": source_url,
        "license_url": PYTHON_LICENSE_URL,
        "copyright_url": "https://docs.python.org/3.12/copyright.html",
        "reviewed_on": "2026-10-11", "attribution": attribution,
        "changes": "None: original downloaded bytes preserved without modification.",
    }
    for key, filename in (("license", "PSF-2.0.txt"), ("notices", "python-copyright.txt")):
        # Normalize checkout line endings so hashes are portable across Git settings.
        text = assets.joinpath(filename).read_text(encoding="utf-8").replace("\r\n", "\n")
        if not text.strip():
            raise ValueError("bundled license/notice resource is empty")
        result[key] = {"text": text, "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest()}
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
    assets = files("enterprise_mind.ingestion").joinpath("licenses")
    result = {
        "identifier": binding["identifier"], "original_source_url": source_url,
        "license_url": binding["license_url"],
        "copyright_url": binding["copyright_url"],
        "reviewed_on": "2026-10-11", "attribution": attribution,
        "changes": "None: original downloaded bytes preserved without modification.",
        "source_metadata": dict(binding["source_metadata"]),
    }
    for key in ("license", "notices"):
        text = assets.joinpath(binding[key + "_file"]).read_text(
            encoding="utf-8").replace("\r\n", "\n")
        encoded = text.encode("utf-8")
        if not text.strip() or len(encoded) > 65_536:
            raise ValueError("bundled license/notice resource is empty or too large")
        digest = hashlib.sha256(encoded).hexdigest()
        if digest != binding[key + "_sha256"]:
            raise ValueError("bundled terms/notices do not match the reviewed full text")
        result[key] = {"text": text, "sha256": digest}
    return result
