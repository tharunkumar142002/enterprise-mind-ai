"""Bounded HTTPS collection, immutable snapshots and content deduplication."""

import hashlib
import ipaddress
import json
import math
import os
import socket
import ssl
import tempfile
import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from http.client import HTTPException, HTTPSConnection, HTTPResponse
from pathlib import Path
from queue import Empty, Queue
from threading import Thread, Timer
from typing import Any, ContextManager, Protocol
from urllib.parse import urlsplit
from uuid import NAMESPACE_URL, uuid5

from enterprise_mind.ingestion.licensing import license_preservation
from enterprise_mind.ingestion.manifest import (
    FORMAT_MIME_TYPES,
    MAX_DOWNLOAD_BYTES,
    Manifest,
    Source,
    blocked_reasons,
    https_url,
    validate_manifest,
)


class CollectionError(ValueError):
    """Collection rejected or failed; no unsafe fallback is attempted."""


class Response(Protocol):
    status: int
    headers: dict[str, str]

    def read(self, size: int) -> bytes: ...

    def set_timeout(self, timeout: float) -> None: ...


Transport = Callable[[str, float], ContextManager[Response]]


def public_addresses(host: str, timeout: float) -> list[str]:
    """Resolve once within a caller budget, rejecting all non-public destinations."""
    results: Queue[list[str] | Exception] = Queue(maxsize=1)

    def resolve() -> None:
        try:
            addresses = [item[4][0] for item in socket.getaddrinfo(
                host, 443, type=socket.SOCK_STREAM)]
            results.put(addresses)
        except Exception as exc:
            results.put(exc)

    # OS DNS APIs lack a portable timeout; a daemon worker bounds caller waiting.
    Thread(target=resolve, daemon=True).start()
    try:
        answer = results.get(timeout=timeout)
    except Empty as exc:
        raise CollectionError("DNS resolution timed out") from exc
    if isinstance(answer, Exception):
        raise CollectionError("DNS resolution failed") from answer
    if not answer or len(answer) > 64:
        raise CollectionError("DNS returned no addresses or too many addresses")
    for address in answer:
        ip = ipaddress.ip_address(address)
        if not ip.is_global or ip.is_multicast or "%" in address:
            raise CollectionError("DNS returned a non-public destination")
    return list(dict.fromkeys(answer))


class _PinnedHTTPSConnection(HTTPSConnection):
    """Connect to a checked numeric IP while validating TLS against the hostname."""

    def __init__(self, host: str, address: str, timeout: float) -> None:
        self._address = address
        self._deadline = time.monotonic() + timeout
        self._tls_context = ssl.create_default_context()
        super().__init__(host, port=443, timeout=timeout, context=self._tls_context)

    def connect(self) -> None:
        # A numeric address prevents a second hostname lookup/DNS rebinding.
        raw_socket = socket.create_connection((self._address, 443), timeout=self.timeout)
        try:
            remaining = self._deadline - time.monotonic()
            if remaining <= 0:
                raise CollectionError("connection deadline exceeded")
            raw_socket.settimeout(remaining)
            self.sock = self._tls_context.wrap_socket(raw_socket, server_hostname=self.host)
            remaining = self._deadline - time.monotonic()
            if remaining <= 0:
                self.sock.close()
                raise CollectionError("TLS deadline exceeded")
            self.sock.settimeout(remaining)
        except BaseException:
            raw_socket.close()
            raise


@dataclass
class _HTTPResponse:
    response: HTTPResponse
    tls_socket: socket.socket
    status: int
    headers: dict[str, str]

    def read(self, size: int) -> bytes:
        # One underlying read prevents a slow stream from resetting an unbounded
        # read(size) loop's timeout. The collection loop also enforces a deadline.
        return self.response.read1(size)

    def set_timeout(self, timeout: float) -> None:
        self.tls_socket.settimeout(timeout)


@contextmanager
def open_https(url: str, timeout: float) -> Iterator[Response]:
    """Direct TLS only: no proxies, cookies, authentication, redirects or retries."""
    https_url(url, "download URL")
    started = time.monotonic()
    parsed = urlsplit(url)
    assert parsed.hostname is not None
    addresses = public_addresses(parsed.hostname, timeout)
    remaining = timeout - (time.monotonic() - started)
    if remaining <= 0:
        raise CollectionError("request timed out during DNS")
    connection = _PinnedHTTPSConnection(parsed.hostname, addresses[0], remaining)
    response: HTTPResponse | None = None
    active_sockets: list[socket.socket] = []

    def expire() -> None:
        active = active_sockets[-1] if active_sockets else connection.sock
        if active is not None:
            try:
                active.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass

    remaining = timeout - (time.monotonic() - started)
    if remaining <= 0:
        raise CollectionError("request timed out before connection")
    # Interrupt slow HTTP header/chunk framing as well as ordinary body reads.
    watchdog = Timer(remaining, expire)
    watchdog.daemon = True
    watchdog.start()
    try:
        connection.request("GET", parsed.path or "/", headers={
            "User-Agent": "EnterpriseMindAI-Collector/0.1",
            "Accept-Encoding": "identity",
            "Connection": "close",
        })
        tls_socket = connection.sock
        if tls_socket is None:
            raise CollectionError("TLS connection unavailable")
        active_sockets.append(tls_socket)
        remaining = timeout - (time.monotonic() - started)
        if remaining <= 0:
            raise CollectionError("request timed out during connection")
        tls_socket.settimeout(remaining)
        response = connection.getresponse()
        headers: dict[str, str] = {}
        for key, value in response.getheaders():
            key = key.lower()
            if key in headers and key in {"content-length", "content-type", "content-encoding"}:
                raise CollectionError("ambiguous HTTP headers")
            headers[key] = value
        yield _HTTPResponse(response, tls_socket, response.status, headers)
    finally:
        watchdog.cancel()
        if response is not None:
            response.close()
        connection.close()


def safe_path(workspace: Path, path: Path, *, directory: bool = False) -> Path:
    """Confine writes to workspace/data/raw; reject traversal, links and junctions."""
    workspace = workspace.resolve(strict=True)
    candidate = path if path.is_absolute() else workspace / path
    try:
        relative = candidate.relative_to(workspace)
    except ValueError as exc:
        raise CollectionError("output must stay inside workspace/data/raw") from exc
    if relative.parts[:2] != ("data", "raw") or ".." in relative.parts:
        raise CollectionError("output must stay inside workspace/data/raw without traversal")
    cursor = workspace
    for index, part in enumerate(relative.parts):
        cursor = cursor / part
        if cursor.is_symlink() or cursor.is_junction():
            raise CollectionError("symlink/junction output paths are forbidden")
        if cursor.exists():
            needs_directory = directory or index < len(relative.parts) - 1
            if needs_directory and not cursor.is_dir():
                raise CollectionError("output ancestor is not a directory")
            if not needs_directory and not cursor.is_file():
                raise CollectionError("output is not a regular file")
    return cursor


def _write_immutable(workspace: Path, target: Path, data: bytes) -> bool:
    """Publish without overwriting; callers own the per-output collection lock."""
    target = safe_path(workspace, target)
    safe_path(workspace, target.parent, directory=True).mkdir(parents=True, exist_ok=True)
    if target.exists():
        if target.stat().st_size != len(data) or target.read_bytes() != data:
            raise CollectionError("existing immutable record differs from expected content")
        return False
    descriptor, name = tempfile.mkstemp(prefix=".record-", dir=target.parent)
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        # Hard-link publication is atomic and never replaces an existing file.
        os.link(temporary, safe_path(workspace, target))
    finally:
        temporary.unlink(missing_ok=True)
    return True


def _check_existing_blob(path: Path, checksum: str, max_bytes: int) -> None:
    digest = hashlib.sha256()
    total = 0
    with path.open("rb") as stream:
        while chunk := stream.read(64 * 1024):
            total += len(chunk)
            if total > max_bytes:
                raise CollectionError("existing blob exceeds size limit")
            digest.update(chunk)
    if digest.hexdigest() != checksum:
        raise CollectionError("existing blob checksum mismatch")


def _download_one(
    source: Source, manifest: Manifest, workspace: Path, output: Path,
    transport: Transport, timeout: float, max_bytes: int,
    preservation: dict[str, Any] | None = None,
) -> dict[str, Any]:
    limit = min(max_bytes, source.max_bytes)
    staging = safe_path(workspace, output / ".staging", directory=True)
    staging.mkdir(exist_ok=True)
    descriptor, name = tempfile.mkstemp(prefix="document-", dir=staging)
    temporary = Path(name)
    checksum = hashlib.sha256()
    count = 0
    deadline = time.monotonic() + timeout
    try:
        with os.fdopen(descriptor, "wb") as stream, transport(source.url, timeout) as response:
            if response.status != 200:
                raise CollectionError(
                    f"HTTP {response.status}: redirects and non-200 responses rejected"
                )
            content_type = response.headers.get("content-type", "").split(";", 1)[0].strip().lower()
            if content_type not in FORMAT_MIME_TYPES[source.format]:
                raise CollectionError("response Content-Type does not match approved format")
            if response.headers.get("content-encoding", "identity").lower() != "identity":
                raise CollectionError("compressed transfer content is unsupported")
            length = response.headers.get("content-length")
            if length is not None and (not length.isascii() or not length.isdecimal()):
                raise CollectionError("invalid Content-Length")
            if length is not None and int(length) > limit:
                raise CollectionError("declared download size exceeds limit")
            while True:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise CollectionError("download deadline exceeded")
                response.set_timeout(remaining)
                chunk = response.read(min(64 * 1024, limit - count + 1))
                if not chunk:
                    break
                count += len(chunk)
                if count > limit:
                    raise CollectionError("streamed download size exceeds limit")
                checksum.update(chunk)
                stream.write(chunk)
                if length is not None and count == int(length):
                    break
            if count == 0 or (length is not None and count != int(length)):
                raise CollectionError("empty or truncated response")
            stream.flush()
            os.fsync(stream.fileno())
            transfer = {key: response.headers[key] for key in ("etag", "last-modified")
                        if key in response.headers}
        digest = checksum.hexdigest()
        if source.expected_sha256 is not None and digest != source.expected_sha256:
            raise CollectionError("download does not match pinned SHA-256")
        blob = safe_path(workspace, output / "blobs" / digest)
        blob.parent.mkdir(exist_ok=True)
        duplicate_content = blob.exists()
        if duplicate_content:
            _check_existing_blob(blob, digest, limit)
        else:
            os.link(temporary, blob)
        document_id = str(uuid5(NAMESPACE_URL, f"{source.url}#sha256={digest}"))
        record_path = safe_path(workspace, output / "records" / source.source_id /
                                f"{document_id}-{manifest.sha256[:16]}.json")
        if preservation is not None:
            for key in ("license", "notices"):
                artifact = preservation[key]
                path = output / "licenses" / f"{artifact['sha256']}.txt"
                _write_immutable(workspace, path, artifact["text"].encode("utf-8"))
                artifact["path"] = path.relative_to(workspace).as_posix()
        record = {
            "schema_version": 1, "document_id": document_id,
            "source_id": source.source_id, "source_url": source.url,
            "title": source.title, "category": source.category, "format": source.format,
            "collected_at": datetime.now(timezone.utc).isoformat(),
            "license": source.license, "checksum": {"algorithm": "sha256", "value": digest},
            "version": f"sha256:{digest}", "source_version": source.version,
            "access_classification": source.access_classification,
            "provenance": {**source.provenance, "verification": source.verification,
                           "approval": source.approval, "manifest_sha256": manifest.sha256,
                           "original_source_url": source.url,
                           "license_attribution": source.license["attribution"]},
            "size_bytes": count, "blob_path": blob.relative_to(workspace).as_posix(),
            "transfer": transfer,
        }
        if preservation is not None:
            record["license_preservation"] = preservation
            if "source_metadata" in preservation:
                record["provenance"]["source_metadata"] = preservation["source_metadata"]
        if record_path.exists():
            if record_path.stat().st_size > 1_048_576:
                raise CollectionError("existing metadata exceeds size limit")
            existing = json.loads(record_path.read_text(encoding="utf-8"))
            stable_fields = {key: value for key, value in record.items()
                             if key not in {"collected_at", "transfer"}}
            if (not isinstance(existing, dict)
                    or {key: value for key, value in existing.items()
                        if key not in {"collected_at", "transfer"}} != stable_fields):
                raise CollectionError("existing metadata failed integrity checks")
            status = "already_collected"
        else:
            record_bytes = (json.dumps(record, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
            _write_immutable(workspace, record_path, record_bytes)
            status = "collected"
        return {"source_id": source.source_id, "document_id": document_id,
                "status": status, "duplicate_content": duplicate_content,
                "record_path": record_path.relative_to(workspace).as_posix()}
    finally:
        temporary.unlink(missing_ok=True)


def collect(
    manifest: Manifest, source_ids: list[str], *, workspace: Path,
    output: Path = Path("data/raw"), download: bool = False,
    timeout: float = 15, max_bytes: int = 5 * 1024 * 1024,
    transport: Transport = open_https,
) -> list[dict[str, Any]]:
    """Dry-run by default; preflight the entire selection before any writes/network."""
    manifest = validate_manifest(json.loads(manifest.canonical_json))
    if not source_ids or len(set(source_ids)) != len(source_ids):
        raise CollectionError("select at least one unique source ID")
    if type(timeout) not in (int, float) or not math.isfinite(timeout) or not 0 < timeout <= 60:
        raise CollectionError("timeout must be finite, greater than zero and at most 60 seconds")
    if type(max_bytes) is not int or not 1 <= max_bytes <= MAX_DOWNLOAD_BYTES:
        raise CollectionError(f"max_bytes must be 1-{MAX_DOWNLOAD_BYTES}")
    by_id = {source.source_id: source for source in manifest.sources}
    if set(source_ids) - by_id.keys():
        raise CollectionError("selection contains an unknown source ID")
    selection = [by_id[source_id] for source_id in source_ids]
    plan = [{"source_id": source.source_id, "url": source.url,
             "eligible": not blocked_reasons(source, manifest),
             "blocked_reasons": blocked_reasons(source, manifest),
             "max_bytes": min(max_bytes, source.max_bytes)} for source in selection]
    if not download:
        return plan
    if any(not item["eligible"] for item in plan):
        raise CollectionError(
            "download rejected: selected sources must be verified, approved and URL-allowlisted"
        )
    # Local license resources must be available before any download or output writes.
    try:
        preservations = {source.source_id: license_preservation(
            source.source_id, source.url, source.license,
            file_format=source.format, category=source.category) for source in selection}
    except (OSError, ValueError) as exc:
        raise CollectionError(f"license preservation preflight failed: {exc}") from exc
    workspace = workspace.resolve(strict=True)
    output = safe_path(workspace, output, directory=True)
    output.mkdir(parents=True, exist_ok=True)
    lock = safe_path(workspace, output / ".collection.lock")
    try:
        lock_stream = lock.open("x", encoding="utf-8")
    except FileExistsError as exc:
        raise CollectionError(
            "collection lock exists; verify no collector is running before recovery"
        ) from exc
    try:
        with lock_stream:
            lock_stream.write(str(os.getpid()))
            lock_stream.flush()
            _write_immutable(workspace, output / "manifests" / f"{manifest.sha256}.json",
                             manifest.canonical_json)
            results = []
            for source in selection:
                try:
                    results.append(_download_one(source, manifest, workspace, output,
                                                 transport, timeout, max_bytes,
                                                 preservations[source.source_id]))
                except (OSError, HTTPException, ValueError) as exc:
                    raise CollectionError(
                        f"collection failed for {source.source_id}: {exc}"
                    ) from exc
            return results
    finally:
        lock.unlink(missing_ok=True)
