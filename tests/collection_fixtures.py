"""Fictional, in-memory collection fixtures; no external content or credentials."""

import io
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

PAYLOAD = b"FICTIONAL ENTERPRISE RECORD - FOR DEMONSTRATION ONLY\nExample policy.\n"


def manifest_data(*, approved: bool = True) -> dict[str, Any]:
    url = "https://documents.example.com/fictional.txt"
    return {
        "schema_version": 1, "manifest_id": "fictional-test-fixture",
        "researched_on": "2026-10-10", "allowlisted_urls": [url] if approved else [],
        "sources": [{
            "source_id": "fictional-hr", "name": "Fictional HR fixture",
            "title": "FICTIONAL ENTERPRISE RECORD - FOR DEMONSTRATION ONLY",
            "url": url, "category": "human_resources", "format": "txt",
            "version": "fictional-v1", "access_classification": "public",
            "expected_sha256": None, "max_bytes": 1024,
            "license": {"name": "Fictional fixture notice, not an external license claim",
                        "identifier": "LicenseRef-Fictional-Fixture", "url": url,
                        "status": "verified", "attribution": "Fictional example organization",
                        "notes": "Project-authored synthetic test metadata only."},
            "verification": {"status": "verified", "checked_on": "2026-10-10",
                             "evidence_urls": [url], "notes": "Fictional in-memory fixture."},
            "approval": {"approved": approved,
                         "approved_by": "fictional-test-reviewer" if approved else None,
                         "approved_at": "2026-10-10T00:00:00+00:00" if approved else None,
                         "allowed_uses": ["collection_for_rag"] if approved else []},
            "provenance": {"kind": "public_document", "publisher": "Fictional example organization",
                           "notes": "Synthetic fixture; example.com URL is never contacted."},
        }],
    }


class MemoryResponse:
    def __init__(self, payload: bytes, status: int, headers: dict[str, str]) -> None:
        self.stream = io.BytesIO(payload)
        self.status = status
        self.headers = headers

    def read(self, size: int) -> bytes:
        return self.stream.read(size)

    def set_timeout(self, timeout: float) -> None:
        if timeout <= 0:
            raise TimeoutError("synthetic timeout")


class FakeTransport:
    def __init__(self, payload: bytes = PAYLOAD, *, status: int = 200,
                 headers: dict[str, str] | None = None) -> None:
        self.payload = payload
        self.status = status
        self.headers = headers if headers is not None else {"content-type": "text/plain"}
        self.calls: list[str] = []

    @contextmanager
    def __call__(self, url: str, timeout: float) -> Iterator[MemoryResponse]:
        self.calls.append(url)
        response = MemoryResponse(self.payload, self.status, self.headers)
        try:
            yield response
        finally:
            response.stream.close()
