"""Collection tests use only fictional bytes, temporary paths and fake transport."""

import hashlib
import json
import socket
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from typing import Any
from unittest.mock import patch

from collection_fixtures import FakeTransport, MemoryResponse, PAYLOAD, manifest_data
from enterprise_mind.ingestion.collector import (
    CollectionError,
    collect,
    public_addresses,
    safe_path,
)
from enterprise_mind.ingestion.manifest import validate_manifest


class CollectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.workspace = Path(self.temporary.name)
        self.transport = FakeTransport()
        # Any accidental use of the actual network fails the test immediately.
        self.network_guard = patch("socket.create_connection",
                                   side_effect=AssertionError("network forbidden"))
        self.network_guard.start()
        self.addCleanup(self.network_guard.stop)
        self.dns_guard = patch("socket.getaddrinfo", side_effect=AssertionError("DNS forbidden"))
        self.dns_guard.start()
        self.addCleanup(self.dns_guard.stop)

    def run_collection(
        self, data: dict[str, Any] | None = None, *, output: Path = Path("data/raw"),
        timeout: float = 15, max_bytes: int = 5 * 1024 * 1024,
    ) -> list[dict[str, Any]]:
        return collect(validate_manifest(data if data is not None else manifest_data()),
                       ["fictional-hr"], workspace=self.workspace, transport=self.transport,
                       download=True, output=output, timeout=timeout, max_bytes=max_bytes)

    def assert_no_published_documents(self) -> None:
        root = self.workspace / "data/raw"
        self.assertFalse(list(root.glob("blobs/*")))
        self.assertFalse(list(root.glob("records/**/*.json")))
        self.assertFalse(list(root.glob(".staging/*")))
        self.assertFalse((root / ".collection.lock").exists())

    def test_dry_run_never_opens_transport_or_creates_output(self) -> None:
        results = collect(validate_manifest(manifest_data(approved=False)), ["fictional-hr"],
                          workspace=self.workspace, transport=self.transport)
        self.assertFalse(results[0]["eligible"])
        self.assertFalse(self.transport.calls)
        self.assertFalse((self.workspace / "data").exists())

    def test_approval_and_exact_allowlist_are_independent_gates(self) -> None:
        for data in (manifest_data(approved=False), manifest_data()):
            data["allowlisted_urls"] = []
            with self.assertRaises(CollectionError):
                self.run_collection(data)
        self.assertFalse(self.transport.calls)
        self.assertFalse((self.workspace / "data").exists())

    def test_preflight_checks_entire_batch_before_network(self) -> None:
        data = manifest_data()
        second = deepcopy(manifest_data(approved=False)["sources"][0])
        second.update(source_id="fictional-second", url="https://documents.example.com/second.txt")
        data["sources"].append(second)
        with self.assertRaises(CollectionError):
            collect(validate_manifest(data), ["fictional-hr", "fictional-second"],
                    workspace=self.workspace, download=True, transport=self.transport)
        self.assertFalse(self.transport.calls)
        self.assertFalse((self.workspace / "data").exists())

    def test_metadata_checksum_and_provenance(self) -> None:
        result = self.run_collection()[0]
        record = json.loads((self.workspace / result["record_path"]).read_text(encoding="utf-8"))
        expected = hashlib.sha256(PAYLOAD).hexdigest()
        self.assertEqual(record["checksum"]["value"], expected)
        self.assertEqual(record["version"], f"sha256:{expected}")
        self.assertEqual((self.workspace / record["blob_path"]).read_bytes(), PAYLOAD)
        for field in ("source_url", "document_id", "title", "category", "collected_at", "license",
                      "version", "access_classification", "provenance"):
            self.assertIn(field, record)
        self.assertTrue(record["collected_at"].endswith("+00:00"))
        self.assertIn("manifest_sha256", record["provenance"])
        self.assertEqual(record["access_classification"], "public")

    def test_repeated_collection_preserves_record_and_reuses_blob(self) -> None:
        first = self.run_collection()[0]
        record_path = self.workspace / first["record_path"]
        original = record_path.read_bytes()
        second = self.run_collection()[0]
        self.assertEqual(second["status"], "already_collected")
        self.assertTrue(second["duplicate_content"])
        self.assertEqual(first["document_id"], second["document_id"])
        self.assertEqual(original, record_path.read_bytes())
        self.assertEqual(len(list((self.workspace / "data/raw/blobs").iterdir())), 1)

    def test_identical_content_from_distinct_sources_keeps_separate_provenance(self) -> None:
        data = manifest_data()
        second = deepcopy(data["sources"][0])
        second.update(source_id="fictional-second", url="https://documents.example.com/second.txt",
                      category="finance")
        data["sources"].append(second)
        data["allowlisted_urls"].append(second["url"])
        results = collect(validate_manifest(data), ["fictional-hr", "fictional-second"],
                          workspace=self.workspace, download=True, transport=self.transport)
        self.assertNotEqual(results[0]["document_id"], results[1]["document_id"])
        self.assertTrue(results[1]["duplicate_content"])
        self.assertEqual(len(list((self.workspace / "data/raw/blobs").iterdir())), 1)

    def test_size_limits_with_and_without_content_length(self) -> None:
        for headers in ({"content-type": "text/plain"},
                        {"content-type": "text/plain", "content-length": "100"}):
            self.transport = FakeTransport(b"x" * 100, headers=headers)
            with self.assertRaises(CollectionError):
                self.run_collection(max_bytes=10)
            self.assert_no_published_documents()

    def test_rejects_wrong_type_compression_redirects_and_bad_lengths(self) -> None:
        cases = [
            (302, {"content-type": "text/plain", "location": "https://127.0.0.1/secret"}),
            (404, {"content-type": "text/plain"}),
            (200, {"content-type": "application/octet-stream"}),
            (200, {"content-type": "text/plain", "content-encoding": "gzip"}),
            (200, {"content-type": "text/plain", "content-length": "-1"}),
            (200, {"content-type": "text/plain", "content-length": "abc"}),
            (200, {"content-type": "text/plain", "content-length": "999"}),
        ]
        for status, headers in cases:
            with self.subTest(status=status, headers=headers):
                self.transport = FakeTransport(status=status, headers=headers)
                with self.assertRaises(CollectionError):
                    self.run_collection()
                self.assert_no_published_documents()

    def test_accepts_exact_length_and_rejects_empty_body(self) -> None:
        self.transport = FakeTransport(headers={"content-type": "text/plain",
                                                "content-length": str(len(PAYLOAD))})
        self.run_collection()
        self.transport = FakeTransport(b"")
        with self.assertRaises(CollectionError):
            self.run_collection()

    def test_checksum_pin_and_corrupt_existing_blob(self) -> None:
        data = manifest_data()
        data["sources"][0]["expected_sha256"] = "0" * 64
        with self.assertRaises(CollectionError):
            self.run_collection(data)
        self.assert_no_published_documents()
        data["sources"][0]["expected_sha256"] = hashlib.sha256(PAYLOAD).hexdigest()
        result = self.run_collection(data)[0]
        record = json.loads((self.workspace / result["record_path"]).read_text(encoding="utf-8"))
        (self.workspace / record["blob_path"]).write_bytes(b"corrupt synthetic blob")
        with self.assertRaises(CollectionError):
            self.run_collection(data)

    def test_timeout_cleans_staging_and_releases_lock(self) -> None:
        with patch.object(MemoryResponse, "read", side_effect=TimeoutError("synthetic timeout")):
            with self.assertRaises(CollectionError):
                self.run_collection()
        self.assert_no_published_documents()

    def test_elapsed_deadline_rejected_even_when_transport_returns_bytes(self) -> None:
        with patch("enterprise_mind.ingestion.collector.time.monotonic", side_effect=[0, 16]):
            with self.assertRaises(CollectionError):
                self.run_collection()
        self.assert_no_published_documents()

    def test_framing_conflicts_and_malformed_headers_never_publish(self) -> None:
        for framing in (
            {"transfer-encoding": "chunked", "content-length": "1"},
            {"transfer-encoding": "chunked"},
            {"Content-Length": "1", "content-length": "1"},
            {"content-length": "1, 1"}, {"content-length": "+1"},
            {"content-length": "\u0661"}, {"content-length": "9" * 100},
            {"content-length": "1\r\nContent-Length: 2"},
        ):
            with self.subTest(framing=framing):
                self.transport = FakeTransport(headers={"content-type": "text/plain", **framing})
                with self.assertRaises(CollectionError):
                    self.run_collection()
                self.assert_no_published_documents()

    def test_deadline_expiring_during_final_bytes_or_eof_never_publishes(self) -> None:
        original_read = MemoryResponse.read
        for final_read in ("bytes", "eof"):
            now = [0]

            def delayed_read(response, size):
                chunk = original_read(response, size)
                if final_read == "bytes" or not chunk:
                    now[0] = 16
                return chunk

            headers = {"content-type": "text/plain"}
            if final_read == "bytes":
                headers["content-length"] = str(len(PAYLOAD))
            self.transport = FakeTransport(headers=headers)
            with self.subTest(final_read=final_read):
                with patch("enterprise_mind.ingestion.collector.time.monotonic",
                           side_effect=lambda: now[0]):
                    with patch.object(MemoryResponse, "read", delayed_read):
                        with self.assertRaisesRegex(CollectionError, "deadline"):
                            self.run_collection()
                self.assert_no_published_documents()

    def test_deadline_expiring_during_flush_never_publishes(self) -> None:
        now = [0]
        flushes = [0]

        def delayed_fsync(descriptor):
            flushes[0] += 1
            if flushes[0] > 1:
                now[0] = 16

        with patch("enterprise_mind.ingestion.collector.time.monotonic",
                   side_effect=lambda: now[0]):
            # The manifest is published before the per-download budget starts.
            with patch("enterprise_mind.ingestion.collector.os.fsync", delayed_fsync):
                with self.assertRaisesRegex(CollectionError, "deadline"):
                    self.run_collection()
        self.assert_no_published_documents()

    def test_tampered_metadata_rejected(self) -> None:
        result = self.run_collection()[0]
        path = self.workspace / result["record_path"]
        record = json.loads(path.read_text(encoding="utf-8"))
        record["license"]["name"] = "corrupted fictional license"
        path.write_text(json.dumps(record), encoding="utf-8")
        with self.assertRaises(CollectionError):
            self.run_collection()

    def test_invalid_selection_and_limits_do_not_start_transport(self) -> None:
        for ids in ([], ["unknown-source"], ["fictional-hr", "fictional-hr"]):
            with self.assertRaises(CollectionError):
                collect(validate_manifest(manifest_data()), ids, workspace=self.workspace,
                        transport=self.transport, download=True)
        for options in ({"timeout": 0}, {"timeout": float("nan")}, {"max_bytes": 0},
                        {"max_bytes": True}):
            with self.assertRaises(CollectionError):
                self.run_collection(**options)
        self.assertFalse(self.transport.calls)

    def test_traversal_and_external_output_paths_rejected(self) -> None:
        for output in (Path("data/raw/../../escape"), Path("docs"),
                       self.workspace.parent / "outside"):
            with self.assertRaises(CollectionError):
                self.run_collection(output=output)
        self.assertFalse(self.transport.calls)

    def test_symlink_output_rejected_where_supported(self) -> None:
        data = self.workspace / "data"
        data.mkdir()
        try:
            (data / "raw").symlink_to(self.workspace, target_is_directory=True)
        except OSError:
            self.skipTest("symlink creation not permitted on this host")
        with self.assertRaises(CollectionError):
            safe_path(self.workspace, Path("data/raw"), directory=True)

    def test_existing_lock_not_removed_or_overwritten(self) -> None:
        root = self.workspace / "data/raw"
        root.mkdir(parents=True)
        lock = root / ".collection.lock"
        lock.write_text("fictional-other-process", encoding="utf-8")
        with self.assertRaises(CollectionError):
            self.run_collection()
        self.assertEqual(lock.read_text(encoding="utf-8"), "fictional-other-process")
        self.assertFalse(self.transport.calls)

    def test_private_dns_destinations_rejected_without_connections(self) -> None:
        for address in ("127.0.0.1", "10.0.0.1", "169.254.169.254", "::1", "224.0.0.1"):
            answers = [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (address, 443))]
            with patch("socket.getaddrinfo", return_value=answers):
                with self.assertRaises(CollectionError):
                    public_addresses("documents.example.com", 1)
        with patch("socket.getaddrinfo", return_value=[
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("1.1.1.1", 443))
        ]):
            self.assertEqual(public_addresses("documents.example.com", 1), ["1.1.1.1"])


if __name__ == "__main__":
    unittest.main()
